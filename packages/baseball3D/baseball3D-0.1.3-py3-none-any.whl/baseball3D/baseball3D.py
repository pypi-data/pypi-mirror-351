from pix2world import pix2world
import numpy as np
from get_ballPix_coors import get_ballPix_coors_YOLO

def baseball3D(video_path9920, video_path6808):
    pix_coors_9920 = get_ballPix_coors_YOLO(video_path9920)
    pix_coors_6808 = get_ballPix_coors_YOLO(video_path6808)
    size_9920 = pix_coors_9920.shape[0]
    size_6808 = pix_coors_6808.shape[0]
    if(size_9920 > size_6808) :
        pix_coors_9920 = pix_coors_9920[:-(size_9920 - size_6808)]
    elif(size_9920 < size_6808):
        pix_coors_6808 = pix_coors_6808[:-(size_6808 - size_9920)]

    combined = np.hstack((pix_coors_9920, pix_coors_6808))
    print(combined)
    worlds = []
    for i in combined:

        world = pix2world(i[0], i[1], i[2], i[3]).T
        worlds.append(world)
    worlds = np.vstack(worlds)
    print(worlds)
    return worlds