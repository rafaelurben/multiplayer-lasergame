from blocks import Emitter
import numpy as np
import cv2
from playingfield import Map 


width = 3
height = 3

block_size = 100

m = Map(width, height)

# m.change_field(0, 1, 2)
m.change_field(1, 1, 2)





angle = 0
while True:
    data, lasers = m.step()


    image = np.zeros((block_size * height, block_size * width))
    for laser in lasers:
        for line in laser:
            start = [int(line[0][0] * block_size), int(line[0][1] * block_size)]
            end = [int(line[1][0] * block_size), int(line[1][1] * block_size)]

            image = cv2.line(image, start, end, (255,255,255), 1)

    angle += 0.05
    m.update_state(1, 1, (angle, 10))
    cv2.imshow("test", image)
    cv2.waitKey(200)


cv2.destroyAllWindows()