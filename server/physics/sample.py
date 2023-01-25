from blocks import Emitter
import numpy as np
import cv2
from playingfield import Map 
from copy import deepcopy
from random import randint

width = 7
height = 7

block_size = 100

m = Map(width, height)

m.change_field(0, 0, 1)
m.change_field(1, 0, 1)
m.change_field(2, 0, 1)
m.change_field(3, 0, 1)
m.change_field(4, 0, 1)
m.change_field(5, 0, 1)
m.change_field(6, 0, 1)

m.change_field(0, 6, 1)
m.change_field(1, 6, 1)
m.change_field(2, 6, 1)
m.change_field(3, 6, 1)
m.change_field(4, 6, 1)
m.change_field(5, 6, 1)
m.change_field(6, 6, 1)

m.change_field(0, 1, 1)
m.change_field(0, 2, 1)
m.change_field(0, 3, 6)
m.change_field(0, 4, 1)
m.change_field(0, 5, 1)

m.change_field(6, 1, 1)
m.change_field(6, 2, 1)
m.change_field(6, 3, 4)
m.change_field(6, 4, 1)
m.change_field(6, 5, 1) 



m.change_field(3, 3, 2)




bg = np.zeros((block_size * height + 100, block_size * width + 1000, 3))
for w in range(width):
    start = [(w * block_size), 0]
    end = [(w * block_size), (height * block_size)]

    bg = cv2.line(bg, start, end, (255,255,255), 1)
for h in range(height):
    start = [0, (h * block_size)]
    end = [(height*block_size), (h * block_size)]

    bg = cv2.line(bg, start, end, (255,255,255), 1)

angle = 0
while True:
    data, lasers = m.step()


    image = deepcopy(bg)
    # image = bg
    for laser in lasers:
        for idx, line in enumerate(laser):
            start = [int(line[0][0] * block_size), int(line[0][1] * block_size)]
            end = [int(line[1][0] * block_size), int(line[1][1] * block_size)]
            colors = [
                (255,0,0), 
                (0,255,0),
                (0,0,255)
            ]
            image = cv2.line(image, start, end, colors[2], 1)
    angle += 0.05
    m.update_state(3, 3, (angle, 10))
    cv2.imshow("test", image)
    cv2.waitKey(0)



cv2.destroyAllWindows()