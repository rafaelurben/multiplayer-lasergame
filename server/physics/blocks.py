class Empty:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

class Blocked:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

class Emitter:
    def __init__(self, x, y, angle=0, strength=10):
        self.x = x
        self.y = y
        self.angle = angle
        self.strength = strength

    def create_laser_path(self):
        lines = []
        return (lines, end_point, end_angle, end_strength, exit_border)
    
    def get_laser_path(self, point, angle, strength, border):
        # some code
        return (lines, end_point, end_angle, end_strength, exit_border)

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
