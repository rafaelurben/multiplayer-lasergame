import math
from copy import deepcopy

HP_STAGES = 4

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
    
    def round_point(self, point):
        decimals = 1
        point[0] = round(point[0], decimals)
        point[1] = round(point[1], decimals)
        return point

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

        if 0 <= t <= 1 and 0 <= u <= 1:
            new_x = x1 + (t * (x2 - x1))
            new_y = y1 + (t * (y2 - y1))
            return True, [new_x, new_y]
        else:
            return False, None


    def normalize(self, point, border):
        # print(point)
        point[1] = round(point[1], 1)
        point[0] = round(point[0], 1)
        if point[0] == 0:
            point[0] = 1
        elif point[0] == 1:
            point[0] = 0
        if point[1] == 0:
            point[1] = 1
        elif point[1] == 1:
            point[1] = 0
        return point

    def get_path(self, point, angle, border, strength):
        point = self.normalize(point, border)
        outside_point = [point[0] + (2 * math.cos(angle)), point[1] + (2 * (math.sin(angle)))]
        if not point[1] == 0:
            north, p_n = self.line_incersection(point, outside_point, [0,0], [1,0])
            if north:
                # exit_border.append("n")
                end_point = [p_n[0], 0]
        if not point[0] == 1:
            east, p_e = self.line_incersection(point, outside_point, [1,0], [1,1])
            if east:
                # exit_border.append("e")
                end_point = [1, p_e[1]]
        if not point[1] == 1:
            south, p_s = self.line_incersection(point, outside_point, [0,1], [1,1])
            if south:
                # exit_border.append("s")
                end_point = [p_s[0], 1]
        if not point[0] == 0:
            west, p_w = self.line_incersection(point, outside_point, [0,0], [0,1])
            if west:
                # exit_border.append("w")
                end_point = [0, p_w[1]]

        exit_border = []
        end_point = self.round_point(end_point)
        if end_point[0] == 0:
            exit_border.append("w")
        if end_point[1] == 0:
            exit_border.append("n")
        if end_point[0] == 1:
            exit_border.append("e")
        if end_point[1] == 1:
            exit_border.append("s")

        lines = [[point, end_point, strength]]

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
        # print(border, self.angle)
        if self.angle == 0:
            if "e" in border:
                end_point = [0, point[1]]
                angle = math.pi - angle
                exit_border.append("w")
            if "w" in border:
                end_point = [1, point[1]]
                angle = math.pi - angle
                exit_border.append("e")
        elif self.angle == 1:
            if "n" in border:
                end_point = [point[0], 1]
                angle = 2 * math.pi - angle
                exit_border.append("s")
            if "s" in border:
                end_point = [point[0], 0]
                angle = 2 * math.pi - angle
                exit_border.append("n")
        else:
            return ([], [0, 0], angle, strength, [])

        angle = (angle + (2*math.pi))%(2*math.pi)

        lines = []
        return (lines, end_point, angle, strength, exit_border)

class Emitter(Block):
    strength_factor = 1.0005
    strength = 0.001

    def tick(self):
        self.strength *= self.strength_factor

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
        if north:
            end_point = [p_n[0], 0]
        if east:
            end_point = [1, p_e[1]]
        if south:
            end_point = [p_s[0], 1]
        if west:
            end_point = [0, p_w[1]]

        exit_border = []
        end_point = self.round_point(end_point)
        if end_point[0] == 0:
            exit_border.append("w")
        if end_point[1] == 0:
            exit_border.append("n")
        if end_point[0] == 1:
            exit_border.append("e")
        if end_point[1] == 1:
            exit_border.append("s")

        lines = [[point, end_point, self.strength]]
        return (lines, deepcopy(end_point), self.angle, self.strength, exit_border)

    def get_laser_path(self, point, angle, strength, border, laser_team):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        return (lines, end_point, angle, strength, border)




class Receiver(Block):
    def __init__(self):
        super().__init__()
        self.hp_diff = 0

    def get_data(self):
        data = {
            "id" : self.id,
            "team" : self.team,
            "owner" : self.owner,
            "type" : self.type,
            "pos" : self.pos,
            "rotation" : self.angle,
            "is_hit" : self.hp_diff > 0
        }
        return data

    def tick(self):
        # reset hp_diff (will be updated by get_laser_path)
        self.hp_diff = 0

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
        if hit and laser_team == self.team:
            self.hp_diff += strength

        return (lines, end_point, angle, strength, border)

class Wood(Block):
    strength_factor = 0.8

    def __init__(self):
        super().__init__()
        self.max_hp = 0.1
        self.hp = self.max_hp
        self.regeneration = 0.00025
        self.down = False
    
    def get_data(self):
        data = {
            "id" : self.id,
            "team" : self.team,
            "owner" : self.owner,
            "type" : self.type,
            "pos" : self.pos,
            "rotation" : self.angle,
            "hp" : int(self.hp / self.max_hp * HP_STAGES),
            "alive" : not self.down 
        }
        return data

    def tick(self):
        self.hp += self.regeneration
        self.hp = min(self.max_hp, max(0, self.hp))
        if self.max_hp == self.hp:
            self.down = False

    def get_laser_path(self, point, angle, strength, border, laser_team):
        if not self.down:
            self.hp -= strength
            if self.hp < 0:
                self.down = True
            return ([], [0,0], angle, strength, [])
        else:
            lines, end_point, angle, border = self.get_path(point, angle, border, strength)

            return (lines, end_point, angle, strength * self.strength_factor, border)

class Mirror(Block):
    def get_laser_path(self, point, angle, strength, border, laser_team):
        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        mirror_angle = (-self.angle + (math.pi / 2)) % math.pi

        lines, end_point, angle, exit_border = self.get_path(point, angle, border, strength)
        start_point = lines[0][0]

        x1 = start_point[0]
        y1 = start_point[1]
        x2 = end_point[0]
        y2 = end_point[1]
        x3 = 0.5 + 0.5 * (math.cos(mirror_angle))
        y3 = 0.5 + 0.5 * (math.sin(mirror_angle))
        x4 = 0.5 + 0.5 * (-math.cos(mirror_angle))
        y4 = 0.5 + 0.5 * (-math.sin(mirror_angle))

        if (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))) == 0 or (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))) == 0:
            return (lines, end_point, angle, strength, border)

        t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        u = (((x1 - x3) * (y1 - y2)) - ((y1 - y3) * (x1 - x2))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))

        if 0 < t < 1 and 0 < u < 1:
            new_x = x1 + (t * (x2 - x1))
            new_y = y1 + (t * (y2 - y1))

            mirror_point = [new_x, new_y]
            mirror_angle = angle - (2 * (angle - (mirror_angle)))
            outside_point = [mirror_point[0] + (2 * math.cos(mirror_angle)), mirror_point[1] + (2 * (math.sin(mirror_angle)))]
            north, p_n = self.line_incersection(mirror_point, outside_point, [0,0], [1,0])
            east, p_e = self.line_incersection(mirror_point, outside_point, [1,0], [1,1])
            south, p_s = self.line_incersection(mirror_point, outside_point, [0,1], [1,1])
            west, p_w = self.line_incersection(mirror_point, outside_point, [0,0], [0,1])

            if north:
                end_point = [p_n[0], 0]
            if east:
                end_point = [1, p_e[1]]
            if south:
                end_point = [p_s[0], 1]
            if west:
                end_point = [0, p_w[1]]

            exit_border = []
            end_point = self.round_point(end_point)
            if end_point[0] == 0:
                exit_border.append("w")
            if end_point[1] == 0:
                exit_border.append("n")
            if end_point[0] == 1:
                exit_border.append("e")
            if end_point[1] == 1:
                exit_border.append("s")

            lines = [[start_point, mirror_point, strength], deepcopy([mirror_point, end_point, strength])]
            angle = mirror_angle
            angle = (angle + (2*math.pi))%(2*math.pi)


        return (lines, end_point, angle, strength, exit_border)

class Glass(Block):
    strength_factor = 0.8
    def get_laser_path(self, point, angle, strength, border, laser_team):
        lines, end_point, angle, border = self.get_path(point, angle, border, strength)
        return (lines, end_point, angle, strength * self.strength_factor, border)



