import cv2
import numpy as np
from get_ballPix_coors import get_ballPix_coors
from get_ballPix_coors import get_ballPix_coors_YOLO
from pix2world import pix2world
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import find_all_body_points
import board
import baseball3D

video_path9920 = "D:/GoProMocapSystem_Released/server/data/202505040033/synchronized/baseball/9920/GX010079_cut_baseball.MP4"
video_path6808 = "D:/GoProMocapSystem_Released/server/data/202505040033/synchronized/baseball/6808/GX010077_cut_baseball.MP4"
worlds = baseball3D.baseball3D(video_path9920, video_path6808)

X, Y, Z = worlds[:, 0], worlds[:, 1], worlds[:, 2]

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# 繪製 3D 散點圖
ax.scatter(X, Y, Z, c=Z, cmap='viridis', marker='o', alpha=0.8) # 待 yolo 完成
find_all_body_points.find_all_body_worldpoints("D:/GoProMocapSystem_Released/server/data/202505040033/synchronized/body/9920/GX010079_cut.MP4", "D:/GoProMocapSystem_Released/server/data/202505040033/synchronized/body/6808/GX010077_cut.MP4", ax)
board.find_kzone("D:/GoProMocapSystem_Released/server/data/202505040033/synchronized/body/9920/GX010079_cut.MP4","D:/GoProMocapSystem_Released/server/data/202505040033/synchronized/body/6808/GX010077_cut.MP4", ax)

# 設定標籤
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Scatter Plot')

plt.show()