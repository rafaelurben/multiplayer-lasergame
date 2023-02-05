import math
from copy import deepcopy

class Block:
    def __init__(self):
        self.id = None
        self.owner = None
        self.team = None
        self.type = None
        self.pos = None
        self.angle = None

    def get_data(self):
        data = {
            "id" : self.id,
            "team" : self.team,
            "owner" : self.owner,
            "type" : self.type,
            "pos" : self.pos,
            "rotation" : self.angle
        }
        return data

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
    
    def get_path(self, point, angle, border, strength):
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

       
        lines = [start_point, end_point, strength]
        return ([lines], deepcopy(end_point), angle, border)

    def tick(self):
        pass

class Empty(Block):
    def get_laser_path(self, point, angle, strength, border):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        return (lines, end_point, angle, strength, border)

class Wall(Block):
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
    strength = 1

    def update_state(self, new_state):
        self.angle = new_state[0]
        self.strength = new_state[1]

    def create_laser_path(self):
        line = [[0.5, 0.5]]

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


        line.append(deepcopy(end_point))
        line.append(self.strength)
        lines = [line]

        return (lines, end_point, self.angle, self.strength, exit_border)
        
    def get_laser_path(self, point, angle, strength, border):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        return (lines, end_point, angle, strength, border)




class Receiver(Block):
    def get_laser_path(self, point, angle, strength, border):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        if ((math.pi / 4) * 7) <= self.angle or self.angle <= (math.pi / 4):
            if end_point[0] == 0 and 0.25 <= end_point[1] <= 0.75:
                print("hit")
                border = []
        if (math.pi / 4) <= self.angle <= ((math.pi / 4) * 3):
            if 0.25 <= end_point[0] <= 0.75 and end_point[1] == 0:
                print("hit")
                border = []
        if ((math.pi / 4) * 3) <= self.angle <= ((math.pi / 4) * 5):
            if end_point[0] == 1 and 0.25 <= end_point[1] <= 0.75:
                print("hit")
                border = []
        if ((math.pi / 4) * 5) <= self.angle <= ((math.pi / 4) * 7):
            if 0.25 <= end_point[0] <= 0.75 and end_point[1] == 1:
                print("hit")
                border = []

        return (lines, end_point, angle, strength, border)

class Wood(Block):
    def __init__(self):
        super().__init__()
        self.hp = 10
        self.regeneration = 0.1
        self.cooldown = 5

    def tick(self):
        self.hp += self.regeneration

    def get_laser_path(self, point, angle, strength, border):
        if self.hp > 0:
            self.hp -= strength
            if self.hp < 0:
                self.hp = -self.cooldown
            return ([], [0,0], angle, strength, [])
        else:
            lines, end_point, angle, border = self.get_path(point, angle, border, strength)
            
            return (lines, end_point, angle, strength, border)

class Mirror(Block):
    def update_state(self, new_state):
        self.angle = new_state[0]

    def line_incersection(self, p1, p2, p3, p4):
        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
        x3 = p3[0]
        y3 = p3[1]
        x4 = p4[0]
        y4 = p4[1]
        
        t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        u = (((x1 - x3) * (y1 - y2)) - ((y1 - y3) * (x1 - x2))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))

        if 0 < t < 1 and 0 < u < 1:
            new_x = x1 + (t * (x2 - x1))
            new_y = y1 + (t * (y2 - y1))
            return True, [new_x, new_y]
        else:
            return False, None


    def get_laser_path(self, point, angle, strength, border):
        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        start_point = lines[0][0]

        x1 = start_point[0]
        y1 = start_point[1]
        x2 = end_point[0]
        y2 = end_point[1]
        x3 = 0.5 + 0.5 * (math.cos(self.angle))
        y3 = 0.5 + 0.5 * (math.sin(self.angle))
        x4 = 0.5 + 0.5 * (-math.cos(self.angle))
        y4 = 0.5 + 0.5 * (-math.sin(self.angle))

        if (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))) == 0 or (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))) == 0:
            return (lines, end_point, angle, strength, border)
        
        t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        u = (((x1 - x3) * (y1 - y2)) - ((y1 - y3) * (x1 - x2))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))

        if 0 < t < 1 and 0 < u < 1:
            new_x = x1 + (t * (x2 - x1))
            new_y = y1 + (t * (y2 - y1))

            mirror_point = [new_x, new_y]
            mirror_angle = angle - (2 * (angle - (self.angle)))
            outside_point = [mirror_point[0] + (2 * math.cos(mirror_angle)), mirror_point[1] + (2 * (math.sin(mirror_angle)))]
            north, p_n = self.line_incersection(mirror_point, outside_point, [0,0], [1,0])
            east, p_e = self.line_incersection(mirror_point, outside_point, [1,0], [1,1])
            south, p_s = self.line_incersection(mirror_point, outside_point, [0,1], [1,1])
            west, p_w = self.line_incersection(mirror_point, outside_point, [0,0], [0,1])

            border = []
            if north:
                border.append("n")
                end_point = [p_n[0], 0]
            if east:
                border.append("e")
                end_point = [1, p_e[1]]
            if south:
                border.append("s")
                end_point = [p_s[0], 1]
            if west:
                border.append("w")
                end_point = [0, p_w[1]]

            lines = [[start_point, mirror_point, strength], deepcopy([mirror_point, end_point, strength])]
            angle = mirror_angle
            angle = (angle + (2*math.pi))%(2*math.pi)



        return (lines, end_point, angle, strength, border)

class Glass(Block):
    strength_factor = 0.8
    def get_laser_path(self, point, angle, strength, border):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        return (lines, end_point, angle, strength * self.strength_factor, border)