from empty import Empty

class Map:
    block_id_dic = {
        0 : Empty,
        1 : 0,
        2 : 0,
        3 : 0,
        4 : 0,
        5 : 0,
        6 : 0
    }
    def __init__(self, mapwidth, mapheight):
        self.map = [[Empty for _ in range(mapwidth)] for _ in range(mapheight)]

    def step(self):
        self.update_lasers()
        return self.get_data()

    def update_lasers(self):
        pass

    def get_data(self):
        pass

    def change_field(self, field_x, field_y, block_id):
        self.map[field_x][field_y] = self.block_id_dic[block_id]

    def update_state(self, field_x, field_y, new_state):
        pass

    def move(self, field_x, field_y, direction):
        pass
