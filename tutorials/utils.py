import matplotlib.pyplot as plt
import pyfmm
import time
import cv2
import numpy as np
import imutils
import random

def convert2list(img):
    height, width = img.shape
    maze = np.zeros((height, width), np.uint8)
    for i in range(width):
        for j in range(height):
            maze[j][i] = 1 if img[j][i] > 0 else 0

    return maze.tolist()

def img2binList(img, lenWidth, GRID_SIZE=50, verbose=1):
    global DISTANCECOSTMAP
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, gray = cv2.threshold(gray, 112, 255, cv2.THRESH_BINARY_INV)
    if verbose:
        showmaze = cv2.resize(gray, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow("img", showmaze)
        cv2.waitKey(0)

    cnts = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    locs = []

    height, width = gray.shape
    tmp = np.zeros((height, width), np.uint8)

    idxLargest = 0
    areaLargest = 0
    # loop over the contours
    for (i, c) in enumerate(cnts):
        # compute the bounding box of the contour, then use the
        # bounding box coordinates to derive the aspect ratio
        (x, y, w, h) = cv2.boundingRect(c)
        if w * h > areaLargest:
            idxLargest = i
            areaLargest = w * h
        cv2.rectangle(tmp, (x, y), (x + w, y + h), (255, 0, 0), 2)

    if verbose:
        # print("found largest contour outline")
        showmaze = cv2.resize(tmp, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow("img", showmaze)
        cv2.waitKey(0)

    # print("cropping image as largest contour")
    (x, y, w, h) = cv2.boundingRect(cnts[idxLargest])
    gray = gray[y:y + h, x:x + w]

    if verbose:
        showmaze = cv2.resize(gray, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow("img", showmaze)
        cv2.waitKey(0)

    mapWidth = (int)(lenWidth // GRID_SIZE)
    mapHeight = (int)((h / w) * lenWidth // GRID_SIZE)
    print("the map will be created by the size: " + str(mapWidth) + " X " + str(mapHeight))

    resized_gray = imutils.resize(gray, width=mapWidth)  # resize the map for convolution
    _, resized_gray = cv2.threshold(resized_gray, 1, 255, cv2.THRESH_BINARY)
    if verbose:
        showmaze = cv2.resize(resized_gray, None, fx=4.7, fy=4.7, interpolation=cv2.INTER_NEAREST)
        cv2.imshow("img", showmaze)
        cv2.waitKey(0)
    maze = convert2list(resized_gray)
    my_maze = np.array(maze)
    solution = pyfmm.march(my_maze == 1, batch_size=100000)[0] # NOTE : white area means walkable area
    DISTANCECOSTMAP = solution

    # cv2.destroyAllWindows()
    return maze, DISTANCECOSTMAP

def convert2meter(path, scale=0.2):
    """convert the path in meter scale"""
    """in general, one grid represent 0.5 meter"""
    path_list = [list(elem) for elem in path]
    metered_path = []
    for grid in path_list:
        metered_grid = [i * scale for i in grid]
        metered_path.append(metered_grid)
    return metered_path

def maze2obs(maze, x_w, y_w):
    obstacleList = []
    for i in range(x_w-1):
        for j in range(y_w-1):
            if maze[j][i] == 1:
                obstacleList.append((i, j))
    return obstacleList
