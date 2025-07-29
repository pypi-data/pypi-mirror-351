from typing import List
from sensor_msgs.msg import CameraInfo
from geometry_msgs.msg import Quaternion
from .validate import *
from .interface import *
import numpy as np
import open3d as o3d
import math
from shapely.geometry import Point, Polygon

currentCameraInfo = None
defaultDepth = 0.5 #TODO: Make this value changeble
depthMeanError = 0.05 #TODO: Make this value changeble
fitBox = True # TODO:Make this value changeble
lutTable = None
# descriptionProcessingAlgorithms = {
#     "detection": boundingBoxProcessing,
# }

def __pointCloudProcessing(data: BoundingBoxProcessingData):
    print("point cloud processing not implemented yet")
    raise Exception("point cloud processing not implemented yet")

def __imageDepthProcessing(data: BoundingBoxProcessingData):
    global lutTable, currentCameraInfo
    imageDepth = data.sensor.imageDepth
    data.sensor.setSensorData(cameraInfo=data.sensor.cameraInfo, imageDepth=data.sensor.imageDepth)

    imageDepth = data.sensor.imageDepth
    cameraInfo = data.sensor.cameraInfo
    height, width = imageDepth.shape

    bboxLimits = [int(data.boundingBox2D.center.position.x - data.boundingBox2D.size_x/2), int(data.boundingBox2D.center.position.x + data.boundingBox2D.size_x/2),
                    int(data.boundingBox2D.size_y - data.boundingBox2D.size_y/2), int(data.boundingBox2D.center.position.y + data.boundingBox2D.size_y/2)]


    bboxLimits[0] = bboxLimits[0] if bboxLimits[0] > 0 else 0
    bboxLimits[1] = bboxLimits[1] if bboxLimits[1] < width else width - 1
    bboxLimits[2] = bboxLimits[2] if bboxLimits[2] > 0 else 0
    bboxLimits[3] = bboxLimits[3] if bboxLimits[3] < height else height - 1
    __mountLutTable(cameraInfo) #TODO: Implement this method


    centerDepth = imageDepth[int(data.boundingBox2D.center.position.y)][int(data.boundingBox2D.center.position.x)]
    validateCenterDepth(centerDepth)

    centerDepth/= 1000.
    limits = np.asarray([(bboxLimits[0], bboxLimits[2]), (bboxLimits[1], bboxLimits[3])])
    vertices3D = np.zeros((len(limits), 3))

    if lutTable is None:
        raise Exception("Lut table is not defined")
    vertices3D[:, :2] = lutTable[limits[:, 1]-1, limits[:, 0]-1, :]*centerDepth
    vertices3D[:, 2] = centerDepth
    maxSizeMessage = data.maxSize
    maxSizeVector = np.array([maxSizeMessage.x, maxSizeMessage.y, maxSizeMessage.z])
    descriptionDepth = defaultDepth
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
        vertices3D = np.concatenate((vertices3D - np.array([0, 0, depthMeanError]),vertices3D + np.array([0, 0, descriptionDepth])))
        minBound = np.min(vertices3D, axis=0)
        maxBound = np.max(vertices3D, axis=0)

        if fitBox:
            boxDepths = imageDepth[limits[0, 1]:limits[1, 1], limits[0, 0]:limits[1, 0]]/1000.
            boxLut = lutTable[limits[0, 1]:limits[1, 1], limits[0, 0]:limits[1, 0], :]

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
        boxOrientation = __quaternionFromMatrix(boxRotation)
        boxSize = np.dot(boxSize, boxRotation[:3, :3])

        boundingBox3D = BoundingBox3D()
        boundingBox3D.center.position.x = boxCenter[0]
        boundingBox3D.center.position.y = boxCenter[1]
        boundingBox3D.center.position.z = boxCenter[2]
        boundingBox3D.center.orientation.x = boxOrientation[0]
        boundingBox3D.center.orientation.y = boxOrientation[1]
        boundingBox3D.center.orientation.z = boxOrientation[2]
        boundingBox3D.center.orientation.w = boxOrientation[3]
        boundingBox3D.size.x = boxSize[0]
        boundingBox3D.size.y = boxSize[1]
        boundingBox3D.size.z = boxSize[2]

    return boundingBox3D

# 'def __recognitions3DConcatenate(array_point_cloud, descriptions2d, recog_header, header):
#     output_data = [BoundingBox3D()]

#     descriptions3d = [None]*len(descriptions2d)
#     for i, d in enumerate(descriptions2d):
#         descriptions3d[i] = __createBoundingBox3D(array_point_cloud, d, header)

#     output_data.descriptions = [d3 for d3 in descriptions3d if d3 is not None]
#     return output_data'

def __quaternionFromMatrix(matrix: np.ndarray):
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

def __mountLutTable(cameraInfo: CameraInfo):
    global lutTable, currentCameraInfo
    if lutTable is None or (currentCameraInfo is not None and not validateCompareCameraInfo(currentCameraInfo, cameraInfo)):
        currentCameraInfo = cameraInfo
        K = np.asarray(cameraInfo.k).reshape((3,3))

        fx = 1./K[0,0]
        fy = 1./K[1,1]
        cx = K[0,2]
        cy = K[1,2]

        x_table = (np.arange(0, currentCameraInfo.width) - cx)*fx
        y_table = (np.arange(0, currentCameraInfo.height) - cy)*fy

        x_mg, y_mg = np.meshgrid(x_table, y_table)

        lutTable = np.concatenate((x_mg[:, :, np.newaxis], y_mg[:, :, np.newaxis]), axis=2)

def boundingBoxProcessing(data: BoundingBoxProcessingData, method: str = "image_depth"):
    validateCenter(data.boundingBox2D.center)
    validateSize2D(data.boundingBox2D.size_x, data.boundingBox2D.size_y)
    if method == "point_cloud":
        return __pointCloudProcessing(data)
    elif method == "image_depth":
        return __imageDepthProcessing(data)
    else:
        raise Exception("Method not implemented")

def __poseDepthProcessing(data: BoundingBoxProcessingData) -> list:

    points3D = []

    image_depth = data.sensor.imageDepth
    camera_info = data.sensor.cameraInfo

    global lutTable

    h, w = image_depth.shape
    for X2D, Y2D, score, id in data.pose:
            u = int(X2D)
            v = int(Y2D)

            if u >= w or u < 0 or v >= h or v < 0:
                score = 0.0

                point3D = [0.0,0.0,0.0, score, id]
            else:
                depth = image_depth[v, u]

                if depth <= 0:
                    score = 0.0
                    point3D = [0.0,0.0,0.0, score, id]

                else:
                    depth /= 1000.

                    vertex_3d = np.zeros(3)
                    vertex_3d[:2] = lutTable[v, u, :]*depth
                    vertex_3d[2] = depth

                    point3D = [vertex_3d[0],vertex_3d[1],vertex_3d[2], score, id]

            points3D.append(point3D)
    return points3D

def poseProcessing(data: BoundingBoxProcessingData, method: str = "image_depth") -> np.ndarray:
    if method == "image_depth":
        return __poseDepthProcessing(data)
    else:
        raise NotImplementedError(f"Method {method} not implementeds")
    


def inPolygonFilter(boundingBox3D: BoundingBox3D, polygonVertices: list):
    validateBoundingBox3D(boundingBox3D)
    validatePolygonVertices(polygonVertices)
    polygon = Polygon(polygonVertices)
    point = Point(boundingBox3D.center.position.x, boundingBox3D.center.position.y)
    return polygon.contains(point)
