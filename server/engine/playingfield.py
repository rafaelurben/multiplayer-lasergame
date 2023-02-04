from blocks import Empty, Wall, Emitter, Receiver, Wood, Mirror, Glass
from copy import deepcopy
import math

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
    max_laser_bounces = 100

    def __init__(self, mapwidth, mapheight, players):
        self.width = mapwidth + 2
        self.height = mapheight + 2
        self.map = [[Empty() for x in range(self.width)] for y in range(self.height)]
        self.lasers = []
        self.players = players
        self.teams = {}
        for player in self.players:
            if player["team"] in self.teams:
                self.teams[player["team"]].append(player["id"])
            else:
                self.teams[player["team"]] = [player["id"]]
        self.generate_map()

    def generate_map(self):
        factor_of_filled_blocks = 0.2
        block_set = {
            4 : 1,
            5 : 1,
            6 : 1
        }

        # Border
        for field_x in range(self.width):
            for field_y in range(self.height):
                if field_x == 0 or field_y == 0 or field_x == self.width - 1 or field_y == self.height - 1:
                    self.change_field(field_x, field_y, 1)

        lcm = 1
        for t in self.teams:
            lcm = math.lcm(lcm, len(self.teams[t]))

        expected_n_block_sets_per_team = int((self.width - 2) * (self.height - 2) * factor_of_filled_blocks)
        n_block_sets_per_team = expected_n_block_sets_per_team + (lcm - (expected_n_block_sets_per_team % lcm))
        
        

        



    def change_field(self, field_x, field_y, block_id):
        self.map[field_x][field_y] = self.block_id_dic[block_id]()

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


    def update_state(self, field_x, field_y, new_state):
        self.map[field_x][field_y].update_state(new_state)


    # Actions

    def tick(self) -> None:
        "Called every tick. Updates the score and lasers."

    def handle_controls(self, player_id: int, block_id: int, button: str) -> bool:
        """Returns True if the action was successful. Handles the controls of the player.
        `button` is a string in ['move_up', 'move_down', 'move_left', 'move_right', 'rotate_left', 'rotate_right'].
        """

    # Queries

    def get_score(self) -> float:
        pass

    def get_lasers(self) -> list:
        pass

    def get_map(self) -> list:
        blocks = []
        block = {
            "id" : 0,
            "team" : 0,
            "owner" : 0,
            "type" : 0,
            "pos" : {
                "x" : 0,
                "y" : 0,
            },
            "rotation" : 0
        }
