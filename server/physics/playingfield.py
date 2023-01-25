from blocks import Empty, Wall, Emitter, Receiver, Wood, Mirror, Glass
from copy import deepcopy

class Map:
    block_id_dic = {
        0 : Empty,
        1 : Wall,
        2 : Emitter,
        3 : Receiver,
        4 : Wood,
        5 : Mirror,
        6 : Glass
    }
    max_laser_bounces = 1000

    def __init__(self, mapwidth, mapheight):
        self.map = [[Empty() for x in range(mapwidth)] for y in range(mapheight)]
        self.lasers = []

    def step(self):
        self.update_lasers()
        return self.get_data()

    def update_lasers(self):
        self.lasers = []
        print('')
        
        for row in range(len(self.map)):
            for col in range(len(self.map[0])):
                if type(self.map[row][col]) == Emitter:
                    lines, point, angle, strength, border = self.map[row][col].create_laser_path()
                    y, x = row, col
                    for l in lines:
                        l[0][1] += y
                        l[0][0] += x
                        l[1][0] += x
                        l[1][1] += y
                    laser_path = lines
                    for bounce in range(self.max_laser_bounces):     
                        if "n" in border:
                            y -= 1
                        if "e" in border:
                            x += 1
                        if "s" in border:
                            y += 1
                        if "w" in border:
                            x -= 1
                        
                        if y == len(self.map) or x == len(self.map[0]) or y == -1 or x == -1:
                            break
                        try:
                            lines, point, angle, strength, border = self.map[y][x].get_laser_path(point, angle, strength, border)
                        except Exception as e:
                            print(e)
                            break
                        if len(border) == 0:
                            break
                        for l in lines:
                            l[0][1] += y
                            l[0][0] += x
                            l[1][0] += x
                            l[1][1] += y
                        laser_path += lines
                    self.lasers.append(laser_path)


    def get_data(self):
        return [self.map, self.lasers]

    def change_field(self, field_x, field_y, block_id):
        self.map[field_x][field_y] = self.block_id_dic[block_id]()

    def update_state(self, field_x, field_y, new_state):
        self.map[field_x][field_y].update_state(new_state)

    def move(self, field_x, field_y, direction):
        pass
