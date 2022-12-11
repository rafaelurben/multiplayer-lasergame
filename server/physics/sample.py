from blocks import Emitter
import numpy as np
import cv2
# from map import Map 


# width = 4
# height = 2

# map = Map(width, height)

# map.change_field(0, 1, 3)
# map.change_field(0, 2, 2)




# map.step()



# m = map.map
# for l in m:
#     print(l)




e = Emitter(0, 10)


image = np.zeros((500, 500))
for i in range(100):
    lines, point, angle, strength, border = e.create_laser_path()
    start_point = (50 + 200, 50 + 200)
    end_point = (int(point[0] * 100) + 200, int(point[1] * 100) + 200)
    image = cv2.line(image, start_point, end_point, (255,255,255), 1)



    cv2.imshow("test", image)
    cv2.waitKey(50)

    e.angle += 0.1



cv2.destroyAllWindows()