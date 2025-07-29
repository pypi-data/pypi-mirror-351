from typing import List
from sensor_msgs.msg import CameraInfo
from geometry_msgs.msg import Quaternion
from validate import Validate
from interface import Data, BoundingBox3D, Box, Center, Size, Color
import numpy as np
import open3d as o3d
import math
from shapely.geometry import Point, Polygon

class Image2World(Validate):
    def __init__(self):
        super().__init__()
        
        self.currentCameraInfo = None
        self.lutTable = None
        self.defaultDepth = 0.5 #TODO: Make this value changeble
        self.depthMeanError = 0.05 #TODO: Make this value changeble
        self.fitBox = True # TODO:Make this value changeble
        descriptionProcessingAlgorithms = {
            "detection": self.boundingBoxProcessing,
        }

    def __pointCloudProcessing(self, data: Data):
        print("point cloud processing not implemented yet")
        pass

    def __imageDepthProcessing(self, data: Data):
        data.sensor.setSensorData(cameraInfo=data.sensor.cameraInfo, image=data.sensor.imageDepth)

        imageDepth = data.sensor.imageDepth
        cameraInfo = data.sensor.cameraInfo
        height, width = imageDepth.shape

        bboxLimits = [int(data.boundingBox2D.center.x - data.boundingBox2D.size.width/2), int(data.boundingBox2D.center.x + data.boundingBox2D.size.width/2), 
                       int(data.boundingBox2D.size.height - data.boundingBox2D.size.height/2), int(data.boundingBox2D.center.y + data.boundingBox2D.size.height/2)]
        
        bboxLimits[0] = bboxLimits[0] if bboxLimits[0] > 0 else 0
        bboxLimits[1] = bboxLimits[1] if bboxLimits[1] < width else width - 1
        bboxLimits[2] = bboxLimits[2] if bboxLimits[2] > 0 else 0
        bboxLimits[3] = bboxLimits[3] if bboxLimits[3] < height else height - 1
        self.__mountLutTable(cameraInfo) #TODO: Implement this method

                
        centerDepth = imageDepth[int(data.boundingBox2D.center.y)][int(data.boundingBox2D.center.x)]
        self.__validateCenterDepth(centerDepth)
        
        centerDepth/= 1000.
        limits = np.asarray([(bboxLimits[0], bboxLimits[2]), (bboxLimits[1], bboxLimits[3])])
        vertices3D = np.zeros((len(limits), 3))

        vertices3D[:, :2] = self.lut_table[limits[:, 1], limits[:, 0], :]*centerDepth
        vertices3D[:, 2] = centerDepth
        maxSizeMessage = data.boundingBox2D.maxSize
        maxSizeVector = np.array([maxSizeMessage.x, maxSizeMessage.y, maxSizeMessage.z])
        descriptionDepth = self.defaultDepth
        if np.any(maxSizeVector == np.zeros(3)):
                raise Warning("Max size is not defined")
        else:
            sizeX, sizeY = vertices3D[1, :2] - vertices3D[0, :2]
            
            differenceError1 = (np.abs(maxSizeVector - sizeX)).tolist()
            sortedDifferencesIndex1 = sorted(zip(differenceError1, range(3)))
            differenceError2 = (np.abs(maxSizeVector - sizeY)).tolist()
            sortedDifferencesIndex2 = sorted(zip(differenceError2, range(3)))

            if sortedDifferencesIndex1[0][1] == sortedDifferencesIndex2[0][1]:
                if sortedDifferencesIndex1[0][0] < sortedDifferencesIndex2[0][0]:
                    sortedDifferencesIndex2[0] = sortedDifferencesIndex2[1]
                else:
                    sortedDifferencesIndex1[0] = sortedDifferencesIndex1[1]
            descriptionDepthId = list(set(range(3)) - set([sortedDifferencesIndex1[0][1], sortedDifferencesIndex2[0][1]]))[0]
            descriptionDepth = maxSizeVector[descriptionDepthId]
            vertices3D = np.concatenate((vertices3D - np.array([0, 0, self.depthMeanError]),vertices3D + np.array([0, 0, descriptionDepth])))
            minBound = np.min(vertices3D, axis=0)
            maxBound = np.max(vertices3D, axis=0)

            if self.fitBox:
                boxDepths = imageDepth[limits[0, 1]:limits[1, 1], limits[0, 0]:limits[1, 0]]/1000.
                boxLut = self.lut_table[limits[0, 1]:limits[1, 1], limits[0, 0]:limits[1, 0], :]

                boxPoints = np.zeros((boxDepths.size, 3))

                boxPoints[:, 0] = boxLut[:, :, 0].flatten()*boxDepths.flatten()
                boxPoints[:, 1] = boxLut[:, :, 1].flatten()*boxDepths.flatten()
                boxPoints[:, 2] = boxDepths.flatten()

                boxPoints = boxPoints[boxPoints[:, 2] > 0]
                boxPoints = boxPoints[np.logical_and(np.all(boxPoints > minBound, axis=1),
                                                    np.all(boxPoints < maxBound, axis=1))]
                
                boxPcd = o3d.geometry.PointCloud()
                boxPcd.points = o3d.utility.Vector3dVector(boxPoints)

                boxPcd, _ = boxPcd.remove_statistical_outlier(20, 2.0)

                # TODO: add a clustering algorithm and pick the closest cluster 

                box = o3d.geometry.AxisAlignedBoundingBox().create_from_points(boxPcd.points)
            
            else:
                box = o3d.geometry.AxisAlignedBoundingBox(minBound, maxBound)

            meanColor = np.array([0, 0, 0])

            boxCenter = box.get_center()
            boxSize = box.get_max_bound() - box.get_min_bound()
            boxRotation = np.eye(4,4)
            boxOrientation = self.__quaternionFromMatrix(boxRotation)
            boxSize = np.dot(boxSize, boxRotation[:3, :3])

            boundingBox3D = BoundingBox3D()

            boundingBox2D = data.boundingBox2D,
            box = Box(
                    center = Center(x=boxCenter[0], y=boxCenter[1], z=boxCenter[2]),
                    orientation = Quaternion(x=boxOrientation[0], y=boxOrientation[1], z=boxOrientation[2], w=boxOrientation[3]),
                    size = Size(width=boxSize[0], height=boxSize[1], depth=boxSize[2]))
            boundingBox3D.__setData(boundingBox2D[0], box)

 
        return BoundingBox3D
    
    # 'def __recognitions3DConcatenate(self, array_point_cloud, descriptions2d, recog_header, header):
    #     output_data = [BoundingBox3D()]

    #     descriptions3d = [None]*len(descriptions2d)
    #     for i, d in enumerate(descriptions2d):
    #         descriptions3d[i] = self.__createBoundingBox3D(array_point_cloud, d, header)

    #     output_data.descriptions = [d3 for d3 in descriptions3d if d3 is not None]
    #     return output_data'

    def __quaternionFromMatrix(self, matrix: np.ndarray):
        q = np.empty((4, ), dtype=np.float64)
        M = np.array(matrix, dtype=np.float64, copy=False)[:4, :4]
        t = np.trace(M)
        if t > M[3, 3]:
            q[3] = t
            q[2] = M[1, 0] - M[0, 1]
            q[1] = M[0, 2] - M[2, 0]
            q[0] = M[2, 1] - M[1, 2]
        else:
            i, j, k = 0, 1, 2
            if M[1, 1] > M[0, 0]:
                i, j, k = 1, 2, 0
            if M[2, 2] > M[i, i]:
                i, j, k = 2, 0, 1
            t = M[i, i] - (M[j, j] + M[k, k]) + M[3, 3]
            q[i] = t
            q[j] = M[i, j] + M[j, i]
            q[k] = M[k, i] + M[i, k]
            q[3] = M[k, j] - M[j, k]
        q *= 0.5 / math.sqrt(t * M[3, 3])
        return q
        
    def __mountLutTable(self, cameraInfo: CameraInfo):
        if self.lut_table is None or (self.currentCameraInfo is not None and not self.__validateCompareCameraInfo(self.currentCameraInfo, cameraInfo)):
            self.currentCameraInfo = cameraInfo
            K = np.asarray(cameraInfo.K).reshape((3,3))

            fx = 1./K[0,0]
            fy = 1./K[1,1]
            cx = K[0,2]
            cy = K[1,2]

            x_table = (np.arange(0, self.currentCameraInfo.width) - cx)*fx 
            y_table = (np.arange(0, self.currentCameraInfo.height) - cy)*fy

            x_mg, y_mg = np.meshgrid(x_table, y_table)

            self.lut_table = np.concatenate((x_mg[:, :, np.newaxis], y_mg[:, :, np.newaxis]), axis=2)

    def boundingBoxProcessing(self, data: Data, method: str = "image_depth"):
        self.__validateCenter(data.boundingBox2D.center)
        self.__validateSize(data.boundingBox2D.size)
        if method == "point_cloud":
            return self.__pointCloudProcessing(data)
        elif method == "image_depth":
            self.__imageDepthProcessing(data)
    
    def inPolygonFilter(self, boundingBox3D: BoundingBox3D, polygonVertices: list):
        self.__validateBoundingBox3D(boundingBox3D)
        self.__validatePolygonVertices(polygonVertices)
        polygon = Polygon(polygonVertices)
        point = Point(boundingBox3D.box.center.x, boundingBox3D.box.center.y)
        return polygon.contains(point)