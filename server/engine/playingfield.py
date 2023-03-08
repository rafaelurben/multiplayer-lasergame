from .blocks import Empty, Wall, Emitter, Receiver, Wood, Mirror, Glass
from .utils import same_inclination
from copy import deepcopy
import math
import random

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
        self.map = [[Empty() for y in range(self.height)] for x in range(self.width)]
        self.lasers = []
        self.players = players
        self.teams = {}
        self.unused_id = 0
        for player in self.players:
            if player["team"] in self.teams:
                self.teams[player["team"]].append(player["id"])
            else:
                self.teams[player["team"]] = [player["id"]]
        self.generate_map()
        self.score = 0.5

        self.last_score = None
        self.last_blocks = None
        self.last_lasers = None

    def generate_map(self):
        factor_of_filled_blocks = 0.02
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

        # receivers and emitters
        y_emitter = int(self.height * (1 / 3))
        y_receiver = int(self.height * (2 / 3))
        self.change_field(field_x=1, field_y=y_emitter, block_id=2, team=0, angle=0)
        self.change_field(field_x=self.width-2, field_y=y_emitter, block_id=2, team=1, angle=math.pi)

        self.change_field(field_x=1, field_y=y_receiver, block_id=3, team=1, angle=0)
        self.change_field(field_x=self.width-2, field_y=y_receiver, block_id=3, team=0, angle=math.pi)



        lcm = 1
        for t in self.teams:
            lcm = math.lcm(lcm, len(self.teams[t]))

        expected_n_block_sets_per_team = int((self.width - 2) * (self.height - 2) * factor_of_filled_blocks)
        n_block_sets_per_team = expected_n_block_sets_per_team + (lcm - (expected_n_block_sets_per_team % lcm))
        
        empty_cords = []
        for field_x in range(1, self.width - 1):
            for field_y in range(1, self.height - 1):
                if type(self.map[field_x][field_y]) == Empty:
                    empty_cords.append((field_x, field_y))

        for t in self.teams:
            team = self.teams[t]
            sets_per_player = int(n_block_sets_per_team / len(team))

            for player in team:
                for set in range(sets_per_player):
                    for block_id in block_set:
                        for block in range(block_set[block_id]):
                            field_x, field_y = empty_cords.pop(random.randint(0, len(empty_cords) - 1))
                            self.change_field(field_x, field_y, block_id, t, player)
            
        

    def change_field(self, field_x, field_y, block_id, team=None, owner=None, angle=0):
        new_block = self.map[field_x][field_y] = self.block_id_dic[block_id]()

        new_block.id = self.unused_id
        new_block.owner = owner
        new_block.team = team
        new_block.type = block_id
        new_block.pos = {
            "x" : field_x - 1,
            "y" : field_y - 1
        }
        new_block.angle = angle

        self.unused_id += 1


    def update_lasers(self):
        self.lasers = []
        # print('')

        for row in range(len(self.map)):
            for col in range(len(self.map[0])):
                if type(self.map[row][col]) == Emitter:
                    lines, point, angle, strength, border = self.map[row][col].create_laser_path()
                    x, y = row, col
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
                        
                        
                        if x == len(self.map) or y == len(self.map[0]) or x == -1 or y == -1:
                            break
                        # lines, point, angle, strength, border = self.map[x][y].get_laser_path(point, angle, strength, border, self.map[row][col].team)

                        try:
                            lines, point, angle, strength, border = self.map[x][y].get_laser_path(point, angle, strength, border, self.map[row][col].team)
                            # print(lines)
                        except Exception as e:
                            print(e)
                            break
                        for l in lines:
                            l[0][1] += y
                            l[0][0] += x
                            l[1][0] += x
                            l[1][1] += y
                        laser_path += lines
                        if len(border) == 0:
                            break
                    self.lasers.append({
                        "team" : self.map[row][col].team,
                        "laser" : laser_path
                    })


    def get_data(self):
        return [self.map, self.lasers]


    def update_state(self, field_x, field_y, new_state):
        self.map[field_x][field_y].update_state(new_state)


    # Actions

    def tick(self) -> None:
        "Called every tick. Updates the score and lasers."
        for field_x in range(1, self.width - 1):
            for field_y in range(1, self.height - 1):
                self.map[field_x][field_y].tick()
        self.update_lasers()

        for field_x in range(1, self.width - 1):
            for field_y in range(1, self.height - 1):
                if type(self.map[field_x][field_y]) == Receiver:
                    if self.map[field_x][field_y].team == 0:
                        self.score += self.map[field_x][field_y].hp_diff
                    else:
                        self.score -= self.map[field_x][field_y].hp_diff
        self.score = min(1, max(self.score, 0))

    def handle_controls(self, player_id: int, block_id: int, button: str) -> bool:
        """Returns True if the action was successful. Handles the controls of the player.

        `button` is a string in ['move_up', 'move_down', 'move_left', 'move_right', 'rotate_left', 'rotate_right'].
        """
        rotation_angle = math.pi / 16
        for field_x in range(1, self.width - 1):
            for field_y in range(1, self.height - 1):
                if self.map[field_x][field_y].id == block_id:
                    x = field_x
                    y = field_y
                    block = deepcopy(self.map[field_x][field_y])
                    if not block.owner == player_id:
                        return False
        if button == "move_up":
            if type(self.map[x][y-1]) == Empty:
                block.pos["y"] -= 1
                self.map[x][y-1] = block
                self.map[x][y] = Empty()
                return True
        elif button == "move_down":
            if type(self.map[x][y+1]) == Empty:
                block.pos["y"] += 1
                self.map[x][y+1] = block
                self.map[x][y] = Empty()
                return True
        elif button == "move_left":
            if type(self.map[x-1][y]) == Empty:
                block.pos["x"] -= 1
                self.map[x-1][y] = block
                self.map[x][y] = Empty()
                return True
        elif button == "move_right":
            if type(self.map[x+1][y]) == Empty:
                block.pos["x"] += 1
                self.map[x+1][y] = block
                self.map[x][y] = Empty()
                return True
        elif button == "rotate_left":
            self.map[x][y].angle += rotation_angle
            return True
        elif button == "rotate_right":
            self.map[x][y].angle -= rotation_angle
            return True
        
        return False
        


    # Queries

    def get_score(self, no_changes: bool = False):
        if no_changes:
            return self.score, None
        
        if self.score == self.last_score:
            return self.score, False
        else:
            self.last_score = self.score
            return self.score, True

    def get_lasers(self, no_changes: bool = False):
        lasers = []
        for laser in self.lasers:
            team = laser["team"]
            lines = []
            for line in laser["laser"]:
                
                x1, y1, x2, y2, strength = line[0][0]-1, line[0][1]-1, line[1][0]-1, line[1][1]-1, line[2]
                coords = [x1, y1, x2, y2]
                
                if len(lines) > 0 and lines[-1][1] == strength:
                    # If the last line has the same strength, we can merge them together

                    if not lines[-1][0][-2:] == [x1, y1]:
                        # Check if the last line ends at the same point as the new one starts
                        # This should technically never happen if the engine is working properly
                        print("Error: Laser path is not continuous!")

                    if same_inclination(lines[-1][0][-4:], coords):
                        # If the lines have the same inclination, we replace the last end point with the new one
                        lines[-1][0][-2] = x2
                        lines[-1][0][-1] = y2
                    else:
                        # If the lines have different inclinations, we can add the new end point to the last line
                        lines[-1][0] += [x2, y2]
                else:
                    lines.append([coords, strength])
            lasers.append({
                "team" : team,
                "lines" : lines
            })

        if no_changes:
            return lasers, None

        if lasers == self.last_lasers:
            return [], False
        else:
            self.last_lasers = deepcopy(lasers)
            return lasers, True

    def get_map(self, no_changes: bool = False):
        blocks = []
        for field_x in range(1, self.width - 1):
            for field_y in range(1, self.height - 1):
                if not type(self.map[field_x][field_y]) == Empty:
                    blocks.append(self.map[field_x][field_y].get_data())

        if no_changes:
            return blocks, None

        if blocks == self.last_blocks:
            return [], False
        else:
            self.last_blocks = deepcopy(blocks)
            return blocks, True
        
