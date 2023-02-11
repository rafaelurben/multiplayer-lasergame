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
    
    def line_incersection(self, p1, p2, p3, p4):
        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
        x3 = p3[0]
        y3 = p3[1]
        x4 = p4[0]
        y4 = p4[1]

        if (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))) == 0 or (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))) == 0:
            return False, None

        t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        u = (((x1 - x3) * (y1 - y2)) - ((y1 - y3) * (x1 - x2))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        t = round(t, 2)
        u = round(u, 2)
        if 0 <= t <= 1 and 0 <= u <= 1:
            new_x = x1 + (t * (x2 - x1))
            new_y = y1 + (t * (y2 - y1))
            return True, [new_x, new_y]
        else:
            return False, None


    def normalize(self, point, border):
        if "n" in border:
            point = [point[0], 1]
        if "e" in border:
            point = [0, point[1]]
        if "s" in border:
            point = [point[0], 0]
        if "w" in border:
            point = [1, point[1]]
        return point

    def get_path(self, point, angle, border, strength):
        point = self.normalize(point, border)
        outside_point = [point[0] + (2 * math.cos(angle)), point[1] + (2 * (math.sin(angle)))]
        exit_border = []
        if not "s" in border:
            north, p_n = self.line_incersection(point, outside_point, [0,0], [1,0])
            if north:
                exit_border.append("n")
                end_point = [p_n[0], 0]
        if not "w" in border:
            east, p_e = self.line_incersection(point, outside_point, [1,0], [1,1])
            if east:
                exit_border.append("e")
                end_point = [1, p_e[1]]
        if not "n" in border:
            south, p_s = self.line_incersection(point, outside_point, [0,1], [1,1])
            if south:
                exit_border.append("s")
                end_point = [p_s[0], 1]
        if not "e" in border:
            west, p_w = self.line_incersection(point, outside_point, [0,0], [0,1])
            if west:
                exit_border.append("w")
                end_point = [0, p_w[1]]



        lines = [[point, end_point, strength]]
        print(exit_border)

        return (lines, deepcopy(end_point), angle, exit_border)

    def tick(self):
        pass

class Empty(Block):
    def get_laser_path(self, point, angle, strength, border, laser_team):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        return (lines, end_point, angle, strength, border)

class Wall(Block):
    def get_laser_path(self, point, angle, strength, border, laser_team):
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
        point = [0.5, 0.5]
        outside_point = [point[0] + (2 * math.cos(self.angle)), point[1] + (2 * (math.sin(self.angle)))]
        north, p_n = self.line_incersection(point, outside_point, [0,0], [1,0])
        east, p_e = self.line_incersection(point, outside_point, [1,0], [1,1])
        south, p_s = self.line_incersection(point, outside_point, [0,1], [1,1])
        west, p_w = self.line_incersection(point, outside_point, [0,0], [0,1])
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

        lines = [[point, end_point, self.strength]]
        return (lines, deepcopy(end_point), self.angle, self.strength, border)

    def get_laser_path(self, point, angle, strength, border, laser_team):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        return (lines, end_point, angle, strength, border)




class Receiver(Block):
    def __init__(self):
        super().__init__()
        self.damage = 0

    def get_laser_path(self, point, angle, strength, border, laser_team):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        hit = False
        if ((math.pi / 4) * 7) <= self.angle or self.angle <= (math.pi / 4):
            if end_point[0] == 0 and 0.25 <= end_point[1] <= 0.75:
                hit = True
                border = []
        if (math.pi / 4) <= self.angle <= ((math.pi / 4) * 3):
            if 0.25 <= end_point[0] <= 0.75 and end_point[1] == 0:
                hit = True
                border = []
        if ((math.pi / 4) * 3) <= self.angle <= ((math.pi / 4) * 5):
            if end_point[0] == 1 and 0.25 <= end_point[1] <= 0.75:
                hit = True
                border = []
        if ((math.pi / 4) * 5) <= self.angle <= ((math.pi / 4) * 7):
            if 0.25 <= end_point[0] <= 0.75 and end_point[1] == 1:
                hit = True
                border = []
        if hit:
            if not laser_team == self.team:
                self.damage += strength

        return (lines, end_point, angle, strength, border)

class Wood(Block):
    def __init__(self):
        super().__init__()
        self.max_hp = 100
        self.hp = self.max_hp
        self.regeneration = 0.5
        self.down = False

    def tick(self):
        self.hp += self.regeneration
        self.hp = min(self.max_hp, self.hp)
        if self.max_hp == self.hp:
            self.down = True

    def get_laser_path(self, point, angle, strength, border, laser_team):
        if not self.down:
            self.hp -= strength
            if self.hp < 0:
                self.down = True
            return ([], [0,0], angle, strength, [])
        else:
            lines, end_point, angle, border = self.get_path(point, angle, border, strength)

            return (lines, end_point, angle, strength, border)

class Mirror(Block):
    def update_state(self, new_state):
        self.angle = new_state[0]

    def get_laser_path(self, point, angle, strength, border, laser_team):
        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        self.angle = self.angle % math.pi
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
    def get_laser_path(self, point, angle, strength, border, laser_team):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        return (lines, end_point, angle, strength * self.strength_factor, border)
