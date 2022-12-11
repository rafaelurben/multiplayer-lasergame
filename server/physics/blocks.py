import math

class Empty:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

class Emitter:
    def __init__(self, angle=0, strength=10):
        self.angle = angle
        self.strength = strength

    def create_laser_path(self):
        lines = [[0.5, 0.5]]

        dy = 0.5 * math.tan(self.angle)
        dx = 0.5 * math.tan((math.pi / 2) - self.angle)

        exit_border = []
        normalized_angle = ((self.angle + (math.pi * 2)) % (math.pi * 2))
        if ((math.pi / 4) * 7) <= normalized_angle or normalized_angle <= (math.pi / 4):
            exit_border.append("e")
            end_point = [1, dy + 0.5]
        if (math.pi / 4) <= normalized_angle <= ((math.pi / 4) * 3):
            exit_border.append("s")
            end_point = [dx + 0.5, 1]
        if ((math.pi / 4) * 3) <= normalized_angle <= ((math.pi / 4) * 5):
            exit_border.append("w")
            end_point = [0, 0.5 - dy]
        if ((math.pi / 4) * 5) <= normalized_angle <= ((math.pi / 4) * 7):
            exit_border.append("n")
            end_point = [0.5 - dx, 0]


        lines.append(end_point)

        return (lines, end_point, self.angle, self.strength, exit_border)
    
    def get_laser_path(self, point, angle, strength, border):
        # some code
        return ([lines], end_point, end_angle, end_strength, exit_border)




class Receiver:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

class Wood:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

class Mirror:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

class Glass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)
