from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import Vector3, Quaternion, Pose
from vision_msgs.msg import BoundingBox2D, BoundingBox3D, Pose2D
from std_msgs.msg import ColorRGBA
from cv_bridge import CvBridge
from typing import Union
import numpy as np

bridge = CvBridge()

class Sensor:
  def __init__(self):
    self.imageDepth: np.ndarray  = np.array([])
    self.cameraInfo: CameraInfo = CameraInfo()

  def setSensorData(self, imageDepth: Union[Image, np.ndarray], cameraInfo: CameraInfo):
    if isinstance(imageDepth, (Image)):
      self.imageDepth = bridge.imgmsg_to_cv2(imageDepth, desired_encoding='passthrough')
    else:
      self.imageDepth = imageDepth
    self.cameraInfo = cameraInfo

class BoundingBoxProcessingData:
  def __init__(self,
               sensor: Sensor = Sensor(),
               boundingBox2D: BoundingBox2D = BoundingBox2D(),
               maxSize: Vector3 = Vector3()
               ):
    self.sensor: Sensor = sensor
    self.boundingBox2D: BoundingBox2D = boundingBox2D
    self.maxSize: Vector3 = maxSize
    self.pose : np.ndarray = np.array([])  # array of tuple of (X2D, Y2D, score, id)

  def __setData(self, boundingBox2D: BoundingBox2D, image: Union[Image, np.ndarray], cameraInfo: CameraInfo):
        self.boundingBox2D = boundingBox2D
        self.sensor.setSensorData(image, cameraInfo)
