from engine.blocks import Emitter
import numpy as np
import cv2
from engine.playingfield import Map 
from copy import deepcopy
import random
import math

width = 20
height = 10

block_size = 50

players = [
    {
        "id": 0,
        "name": "Player 1",
        "team": 0
    },
    {
        "id": 1,
        "name": "Player 2",
        "team": 0
    },
    {
        "id": 2,
        "name": "Player 2",
        "team": 1
    },
    {
        "id": 3,
        "name": "Player 2",
        "team": 1
    },
    {
        "id": 4,
        "name": "Player 2",
        "team": 1
    }
]

m = Map(width, height, players)




x = m.change_field(3, 3, 2, team=2)

x = m.change_field(3, 4, 5, team=2, angle=(math.pi/8)*11)
# m.change_field(4, 3, 5)
# m.update_state(4, 3, [2 * random.random() * math.pi])



bg = np.zeros((block_size * height, block_size * width, 3))
for w in range(width):
    start = [(w * block_size), 0]
    end = [(w * block_size), (height * block_size)]

    bg = cv2.line(bg, start, end, (255,255,255), 1)
for h in range(height):
    start = [0, (h * block_size)]
    end = [(width*block_size), (h * block_size)]

    bg = cv2.line(bg, start, end, (255,255,255), 1)

# blocks = m.get_map()
# for block in blocks:
#     m.handle_controls(block["owner"], block["id"], "rotate_right")

blocks, changes = m.get_map()
for block in blocks:
    colors = [
                (255,0,0), 
                (0,255,0),
                (0,0,255),
                (255,255,0), 
                (0,255,255),
                (255,0,255),
                (255,255,255)
            ]
    bg = cv2.circle(bg, (int((block["pos"]["x"] * block_size) + (0.5 * block_size)), int((block["pos"]["y"] * block_size) + (0.5 * block_size))), 20, colors[block["type"]], 5)


angle = 0
while True:
    m.tick()
    lasers, changes = m.get_lasers()

    image = deepcopy(bg)
    # image = bg
    for laser in lasers:
        for idx, line in enumerate(laser["lines"]):
            start = [int(line[0][0] * block_size), int(line[0][1] * block_size)]
            end = [int(line[0][2] * block_size), int(line[0][3] * block_size)]
            s = min(max(1, int(line[1] * 5)), 1)
            colors = [
                (255,0,0), 
                (0,255,0),
                (0,0,255)
            ]
            # print(start, end)
            image = cv2.line(image, start, end, colors[laser["team"]], s)
    angle += 1e-2
    m.update_state(3, 3, (angle, 1))
    cv2.imshow("test", image)
    cv2.waitKey(0)



cv2.destroyAllWindows()