import cv2
import numpy as np
import sympy as sp
from pix2world import pix2world
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from find_kzone_Ztb import find_kzone_Ztb

def find_board_base(ax):
    
    middle9920 = np.array(list(map(int, input("Enter middle point of 9920: ").split())))
    topleft9920 = np.array(list(map(int, input("Enter topleft point of 9920: ").split())))
    topright9920 = np.array(list(map(int, input("Enter topright point of 9920: ").split())))
    bottomleft9920 = np.array(list(map(int, input("Enter bottomleft point of 9920: ").split())))
    bottomright9920 = np.array(list(map(int, input("Enter bottomright point of 9920: ").split())))

    middle6808 = np.array(list(map(int, input("Enter middle point of 6808: ").split())))
    topleft6808 = np.array(list(map(int, input("Enter topleft point of 6808: ").split())))
    topright6808 = np.array(list(map(int, input("Enter topright point of 6808: ").split())))
    bottomleft6808 = np.array(list(map(int, input("Enter bottomleft point of 6808: ").split())))
    bottomright6808 = np.array(list(map(int, input("Enter bottomright point of 6808: ").split())))

    world_middle = pix2world(middle9920[0], middle9920[1], middle6808[0], middle6808[1])
    world_topleft = pix2world(topleft9920[0], topleft9920[1], topleft6808[0], topleft6808[1])
    world_topright = pix2world(topright9920[0], topright9920[1], topright6808[0], topright6808[1])
    world_bottomleft = pix2world(bottomleft9920[0], bottomleft9920[1], bottomleft6808[0], bottomleft6808[1])
    world_bottomright = pix2world(bottomright9920[0], bottomright9920[1], bottomright6808[0], bottomright6808[1])

    # 將點的座標儲存到字典中
    points = {
        'middle': world_middle,
        'topleft': world_topleft,
        'topright': world_topright,
        'bottomright': world_bottomright,
        'bottomleft': world_bottomleft        
    }

    # 提取 x, y, z 座標
    x_coords = [point[0] for point in points.values()]
    y_coords = [point[1] for point in points.values()]
    z_coords = [point[2] for point in points.values()]
    
    # 創建三維圖形
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    # 繪製點
    ax.scatter(x_coords, y_coords, z_coords, color='b')

    # 連線
    x_coords = [float(point[0]) for point in points.values()]
    y_coords = [float(point[1]) for point in points.values()]
    z_coords = [float(point[2]) for point in points.values()]
    # 把第一個點加到最後
    x_coords.append(x_coords[0])
    y_coords.append(y_coords[0])
    z_coords.append(z_coords[0])
    ax.plot(x_coords, y_coords, z_coords, color='blue')
    
    # 標上每個點的座標
    for x, y, z in zip(x_coords, y_coords, z_coords):
        ax.text(float(x), float(y), float(z), f'({float(x):.2f}, {float(y):.2f}, {float(z):.2f})',fontsize=8, color='black')


    # 算最大範圍，強制三軸用一樣的視覺寬度
    # x_min, x_max = min(x_coords), max(x_coords)
    # y_min, y_max = min(y_coords), max(y_coords)
    # z_min, z_max = min(z_coords), max(z_coords)

    # max_range = max(x_max - x_min, y_max - y_min, z_max - z_min) / 2

    # # 中心點（圍繞中心去畫）
    # x_mid = (x_max + x_min) / 2
    # y_mid = (y_max + y_min) / 2
    # z_mid = (z_max + z_min) / 2

    # ax.set_xlim(x_mid - max_range, x_mid + max_range)
    # ax.set_ylim(y_mid - max_range, y_mid + max_range)
    # ax.set_zlim(z_mid - max_range, z_mid + max_range)

    # 重點：設定座標軸比例
    ax.set_box_aspect([1, 1, 1])

    # 假設這是你要框起來的 4 個點（你可以用任意順序）
    verts = [list(zip(x_coords, y_coords, z_coords))]  # 只放一組面（四個點）

    # 建立多邊形
    poly = Poly3DCollection(verts, alpha=0.3, facecolor='cyan', edgecolor='k')

    # 加到圖上
    ax.add_collection3d(poly)

    # 設置軸標籤
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # 顯示圖形
    # plt.show()
    return points

def find_kzone(path9920, path6808, ax):
    points = find_board_base(ax) # 得到本壘板三維座標點
    Ztb = find_kzone_Ztb(path9920, path6808)
    # 提取 x, y, z 座標
    x_coords = [float(point[0]) for point in points.values()]
    y_coords = [float(point[1]) for point in points.values()]
    z_coords_kzone_top = [float(point[2] + Ztb[0]) for point in points.values()] 
    z_coords_kzone_bottom = [float(point[2] + Ztb[1]) for point in points.values()] 

    # 繪製點
    ax.scatter(x_coords, y_coords, z_coords_kzone_top, color='b')
    ax.scatter(x_coords, y_coords, z_coords_kzone_bottom, color='b')

    # 把第一個點加到最後
    x_coords.append(x_coords[0])
    y_coords.append(y_coords[0])
    z_coords_kzone_top.append(z_coords_kzone_top[0])
    z_coords_kzone_bottom.append(z_coords_kzone_bottom[0])

    # points = {
    #     'middle': world_middle,
    #     'topleft': world_topleft,
    #     'topright': world_topright,
    #     'bottomright': world_bottomright,
    #     'bottomleft': world_bottomleft        
    # }

    ax.plot(x_coords, y_coords, z_coords_kzone_top, color='blue')
    ax.plot(x_coords, y_coords, z_coords_kzone_bottom, color='blue')
    ax.plot([x_coords[2], x_coords[3]], [y_coords[2], y_coords[3]], [z_coords_kzone_bottom[2]+(z_coords_kzone_top[2]-z_coords_kzone_bottom[2])/3, z_coords_kzone_bottom[3]+(z_coords_kzone_top[3]-z_coords_kzone_bottom[3])/3], color='blue')
    ax.plot([x_coords[2], x_coords[3]], [y_coords[2], y_coords[3]], [z_coords_kzone_bottom[2]+(z_coords_kzone_top[2]-z_coords_kzone_bottom[2])*(2/3), z_coords_kzone_bottom[3]+(z_coords_kzone_top[3]-z_coords_kzone_bottom[3])*(2/3)], color='blue')
    ax.plot([x_coords[2]+(x_coords[3]-x_coords[2])/3, x_coords[2]+(x_coords[3]-x_coords[2])/3], [y_coords[2]+(y_coords[3]-y_coords[2])/3, y_coords[2]+(y_coords[3]-y_coords[2])/3], [z_coords_kzone_bottom[2], z_coords_kzone_top[2]], color='blue')
    ax.plot([x_coords[2]+(x_coords[3]-x_coords[2])*(2/3), x_coords[2]+(x_coords[3]-x_coords[2])*(2/3)], [y_coords[2]+(y_coords[3]-y_coords[2])*(2/3), y_coords[2]+(y_coords[3]-y_coords[2])*(2/3)], [z_coords_kzone_bottom[2], z_coords_kzone_top[2]], color='blue')

    for i in range(0,6):
        ax.plot([x_coords[i], x_coords[i]], [y_coords[i], y_coords[i]], [z_coords_kzone_top[i], z_coords_kzone_bottom[i]], linewidth=2)

    # 標上每個點的座標
    for x, y, z in zip(x_coords, y_coords, z_coords_kzone_top):
        ax.text(float(x), float(y), float(z), f'({float(x):.2f}, {float(y):.2f}, {float(z):.2f})',fontsize=8, color='black')
    for x, y, z in zip(x_coords, y_coords, z_coords_kzone_bottom):
        ax.text(float(x), float(y), float(z), f'({float(x):.2f}, {float(y):.2f}, {float(z):.2f})',fontsize=8, color='black')

    # 重點：設定座標軸比例
    ax.set_box_aspect([1, 1, 1])

    # 假設這是你要框起來的 4 個點（你可以用任意順序）
    vertstop = [list(zip(x_coords, y_coords, z_coords_kzone_top))]  # 只放一組面（四個點）
    vertsbottom = [list(zip(x_coords, y_coords, z_coords_kzone_bottom))]  # 只放一組面（四個點）

    # 建立多邊形
    polytop = Poly3DCollection(vertstop, alpha=0.3, facecolor='cyan', edgecolor='k')
    polybottom = Poly3DCollection(vertsbottom, alpha=0.3, facecolor='cyan', edgecolor='k')

    # 加到圖上
    ax.add_collection3d(polytop)
    ax.add_collection3d(polybottom)

    # 設置軸標籤
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # 顯示圖形
    # plt.show()
# find_kzone("D:/GoProMocapSystem_Released/server/data/202504142308/9920/general/GX010073_cut.MP4", "D:/GoProMocapSystem_Released/server/data/202504142308/6808/general/GX010072_cut.MP4")
