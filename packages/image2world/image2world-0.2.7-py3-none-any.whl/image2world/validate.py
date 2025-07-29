from .interface import *
import numpy as np
from sensor_msgs.msg import CameraInfo


def validateCenter(center2D: Pose2D):
    if not isinstance(center2D.position.x, (int, float)) or not isinstance(center2D.position.y, (int, float)):
        raise Exception("Center values must be numbers")

def validateCenter3D(center3D: Pose):
    if not isinstance(center3D.position.x, (int, float)) or not isinstance(center3D.position.y, (int, float)) or not isinstance(center3D.position.z, (int, float)):
        raise Exception("Center values must be numbers")

def validateSize2D(size_x: float, size_y: float):
    if not isinstance(size_x, (int, float)) or not isinstance(size_y, (int, float)):
        raise Exception("Size values must be numbers")

def validateSize3D(size: Vector3):
    if not isinstance(size.x, (int, float)) or not isinstance(size.y, (int, float)) or not isinstance(size.z, (int, float)):
        raise Exception("Size values must be numbers")

def validateCenterDepth(centerDepth):
    if centerDepth <= 0:
        raise Exception("Center depth is not valid")

def validateCompareCameraInfo(currentCameraInfo: CameraInfo, cameraInfo: CameraInfo):
    equal = True
    equal = equal and (cameraInfo.width == currentCameraInfo.width)
    equal = equal and (cameraInfo.height == currentCameraInfo.height)
    equal = equal and np.all(np.isclose(np.asarray(cameraInfo.k),
                                        np.asarray(currentCameraInfo.k)))
    return equal

def validateBoundingBox3D(bbox: BoundingBox3D):
    validateCenter3D(bbox.center)
    validateSize3D(bbox.size)
    # TODO: FINISH THIS VALIDATE METHOD

def validatePolygonVertices(vertices):
    if not isinstance(vertices, list):
        raise Exception("Vertices must be a list")
    for vertex in vertices:
        if not isinstance(vertex, Pose):
            raise Exception("Vertices must be Pose objects")
