import cv2
from camera_thread import CameraThread
from config import CAMERAS

cameras = [CameraThread(nome, url) for nome, url in CAMERAS]

for camera in cameras:
    camera.start()

for camera in cameras:
    camera.join()

cv2.destroyAllWindows()