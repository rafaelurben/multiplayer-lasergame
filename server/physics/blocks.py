import math
from copy import deepcopy

class Block:
    def normalize(self, point, angle, border):
        if "n" in border:
            start_point = [0, point[0]]
            angle += 0.5 * math.pi
        if "e" in border:
            start_point = [0, point[1]]
        if "s" in border:
            start_point = [0, 1 - point[0]]
            angle += 1.5 * math.pi
        if "w" in border:
            start_point = [0, 1 - point[1]]
            angle += math.pi

        angle = (angle + (2*math.pi))%(2*math.pi)

        return start_point, angle
    
    def denormalize(self, start_point, end_point, angle, border):
        if "n" in border:
            start_point = [start_point[1], 1]
            end_point = [end_point[1], 1 - end_point[0]]
            angle -= 0.5 * math.pi
        if "e" in border:
            start_point = start_point
            end_point = end_point
        if "s" in border:
            start_point = [1 - start_point[1], 0]
            end_point = [1 - end_point[1], end_point[0]]
            angle -= 1.5 * math.pi
        if "w" in border:
            start_point = [1, 1 - start_point[1]]
            end_point = [1 - end_point[0], 1 - end_point[1]]
            angle -= math.pi
        
        angle = (angle + (2*math.pi))%(2*math.pi)

        return start_point, end_point, angle
    
    def get_path(self, point, angle, border):
        lines = []

        # normalize
        start_point, angle = self.normalize(point, angle, border)

        # get output
        if angle < (math.pi / 2):
            new_y = start_point[1] + math.tan(angle)
            new_x = 1
            if new_y > 1:
                new_y = 1
                new_x = (1-start_point[1]) / math.tan(angle)
        else:
            new_y = start_point[1] + math.tan(angle)
            new_x = 1
            if new_y < 0:
                new_y = 0
                new_x = start_point[1] / -math.tan(angle)

        end_point = [new_x, new_y]


        # denormalize output
        start_point, end_point, angle = self.denormalize(start_point, end_point, angle, border)

        # get output border
        border = []
        if end_point[0] == 0:
            border.append("w")
        if end_point[1] == 0:
            border.append("n")
        if end_point[0] == 1:
            border.append("e")
        if end_point[1] == 1:
            border.append("s")

       
        lines = [start_point, end_point]
        return ([lines], deepcopy(end_point), angle, border)


class Empty(Block):
    def __init__(self):
        pass

    def get_laser_path(self, point, angle, strength, border):
        lines, end_point, angle, border = self.get_path(point, angle, border)
        return (lines, end_point, angle, strength, border)

class Wall(Block):
    def __init__(self):
        pass

    def get_laser_path(self, point, angle, strength, border):
        exit_border = []
        if "n" in border:
            end_point = [point[0], 1]
            angle = 2 * math.pi - angle
            exit_border.append("s")
        if "e" in border:
            end_point = [0, point[1]]
            angle = math.pi - angle
            exit_border.append("w")
        if "s" in border:
            end_point = [point[0], 0]
            angle = 2 * math.pi - angle
            exit_border.append("n")
        if "w" in border:
            end_point = [1, point[1]]
            angle = math.pi - angle
            exit_border.append("e")

        angle = (angle + (2*math.pi))%(2*math.pi)

        lines = []
        return (lines, end_point, angle, strength, exit_border)

class Emitter(Block):
    def __init__(self, angle=0, strength=10):
        self.angle = angle
        self.strength = strength

    def update_state(self, new_state):
        self.angle = new_state[0]
        self.strength = new_state[1]

    def create_laser_path(self):
        lines = [[0.5, 0.5]]

        dy = 0.5 * math.tan(self.angle)
        dx = 0.5 * math.tan((math.pi / 2) - self.angle)

        exit_border = []
        self.angle = ((self.angle + (math.pi * 2)) % (math.pi * 2))
        if ((math.pi / 4) * 7) <= self.angle or self.angle <= (math.pi / 4):
            exit_border.append("e")
            end_point = [1, dy + 0.5]
        if (math.pi / 4) <= self.angle <= ((math.pi / 4) * 3):
            exit_border.append("s")
            end_point = [dx + 0.5, 1]
        if ((math.pi / 4) * 3) <= self.angle <= ((math.pi / 4) * 5):
            exit_border.append("w")
            end_point = [0, 0.5 - dy]
        if ((math.pi / 4) * 5) <= self.angle <= ((math.pi / 4) * 7):
            exit_border.append("n")
            end_point = [0.5 - dx, 0]


        lines.append(deepcopy(end_point))

        return ([lines], end_point, self.angle, self.strength, exit_border)
        
    def get_laser_path(self, point, angle, strength, border):
        lines, end_point, angle, border = self.get_path(point, angle, border)
        return (lines, end_point, angle, strength, border)




class Receiver:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

class Wood(Block):
    def __init__(self):
        self.hp = 1000
        self.cooldown = 100

    def get_laser_path(self, point, angle, strength, border):
        if self.hp > 0:
            self.hp -= strength
            if self.hp < 0:
                self.hp = -self.cooldown
            return ([], [0,0], angle, strength, [])
        else:
            lines, end_point, angle, border = self.get_path(point, angle, border)
            return (lines, end_point, angle, strength, border)

class Mirror(Block):
    def __init__(self, angle=0):
        self.angle = angle

    def update_state(self, new_state):
        self.angle = new_state[0]

    def get_laser_path(self, point, angle, strength, border):
        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        lines, end_point, angle, border = self.get_path(point, angle, border)
        start_point = lines[0][0]

        x1 = start_point[0]
        y1 = start_point[1]
        x2 = end_point[0]
        y2 = end_point[1]
        x3 = 0.5 + 0.5 * (math.cos(self.angle))
        y3 = 0.5 + 0.5 * (math.sin(self.angle))
        x4 = 0.5 + 0.5 * (-math.cos(self.angle))
        y4 = 0.5 + 0.5 * (-math.sin(self.angle))
        
        t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        u = (((x1 - x3) * (y1 - y2)) - ((y1 - y3) * (x1 - x2))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))

        if 0 < t < 1 and 0 < u < 1:
            new_x = x1 + (t * (x2 - x1))
            new_y = y1 + (t * (y2 - y1))

            mirror_point = [new_x, new_y]
            lines = [[start_point, mirror_point], [[x3, y3], [x4, y4]]]
            mirror_angle = angle - (2 * (angle - (self.angle)))
            lines.append([deepcopy(mirror_point), [mirror_point[0] + math.cos(mirror_angle), mirror_point[1] + math.sin(mirror_angle)]])



        

        return (lines, end_point, angle, strength, border)

class Glass(Block):
    def __init__(self):
        self.strength_factor = 0.8

    def get_laser_path(self, point, angle, strength, border):
        lines, end_point, angle, border = self.get_path(point, angle, border)
        return (lines, end_point, angle, strength * self.strength_factor, border)
