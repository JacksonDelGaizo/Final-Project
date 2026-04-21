import random
from tile import Tile
from constants import *
import pygame


class Board:
    def __init__(self, font, board_data=None):
        self.rows = 5
        self.cols = [3, 4, 5, 4, 3]
        self.font = font
        self.board_settle_spots = []
        self.board_road_spots = []
        self.all_settlements = {} #{(x,y):player_id}
        self.all_roads = {} #{(x,y,rotation):player_id}


        if board_data:
            # CLIENT MODE: received data, build sprites
            self.tiles = pygame.sprite.Group()
            self.build_from_data(board_data)
            self.find_settle_spots(board_data)
            self.find_road_spots(board_data)
        else:
            # SERVER MODE: generate first, then find spots
            self.board_data = self.generate()
            self.find_settle_spots(self.board_data)  # ← Use self.board_data
            self.find_road_spots(self.board_data)  # ← Use self.board_data
            self.tiles = None

    def generate(self):
        """Generate raw tile data (no Pygame) — runs on SERVER"""
        board_data = []
        count = 0

        for row in range(self.rows):
            for col in range(self.cols[row]):
                resource = random.choice(reasources)
                reasources.remove(resource)

                if resource != "desert":
                    num = numbers[count]
                    count += 1
                else:
                    num = None  # Desert has no number

                x = (SCREEN_WIDTH // 2) - (self.cols[row] * (TILE_SIZE) // 2) + (col * (TILE_SIZE))
                y = 50 + 100 * row

                board_data.append({
                    "resource": resource,
                    "number": num,
                    "x": x,
                    "y": y
                })

        return board_data

    def build_from_data(self, board_data):
        """Create sprites from tile data — runs on CLIENT"""
        for tile_data in board_data:
            tile = Tile(
                tile_data["resource"],
                tile_data["x"],
                tile_data["y"],
                tile_data["number"],
                self.font
            )
            self.tiles.add(tile)

    def get_tiles_by_number(self, number):
        """Return tiles matching a dice roll"""
        return [tile for tile in self.tiles if tile.number == number]
    def find_settle_spots(self,board_data):
        for tile_data in board_data:

            x_off = 0
            y_off = 0

            for spot in range(1,9):
                the_spot = (tile_data["x"] + x_off, tile_data["y"] + y_off)
                if spot == 1 or spot == 2 or spot == 6 or spot == 7:
                    x_off += 50
                elif spot == 3 or spot == 5:
                    x_off = 0
                    y_off += 50
                elif spot == 4:
                    x_off += 100
                if the_spot in self.board_settle_spots:
                    continue
                else:
                    self.board_settle_spots.append(the_spot)

    def is_blocked(self, spot, min_distance):
        """Check if spot is too close to existing settlement"""
        for existing_settlement in self.all_settlements:
            distance = ((spot[0] - existing_settlement[0]) ** 2 +
                        (spot[1] - existing_settlement[1]) ** 2) ** 0.5
            if distance <= min_distance:
                return True
        return False
    #TODO check and make sure no road collisons player can place on their own road but not other people's


    def get_valid_settlement_spots(self):
        """Return only unblocked spots"""
        return [spot for spot in self.board_settle_spots if not self.is_blocked(spot,50)]

    def find_road_spots(self, board_data):
        for tile_data in board_data:
            x = tile_data["x"]
            y = tile_data["y"]

            # 8 road spots (2 per edge of the square)
            road_spots = [
                # Top edge
                (x + 25, y, "horizontal"),
                (x + 75, y, "horizontal"),
                # Right edge
                (x + 100, y + 25, "vertical"),
                (x + 100, y + 75, "vertical"),
                # Bottom edge
                (x + 75, y + 100, "horizontal"),
                (x + 25, y + 100, "horizontal"),
                # Left edge
                (x, y + 75, "vertical"),
                (x, y + 25, "vertical"),
            ]

            for road_spot in road_spots:
                if road_spot not in self.board_road_spots:
                    self.board_road_spots.append(road_spot)





    def get_valid_road_spots(self):
        return [spot for spot in self.board_road_spots if not self.is_blocked(spot,0)]

    def get_adjacent_settlements(self, road_spot, player_id):
        """Return YOUR settlements adjacent to this road"""
        road_x, road_y, rotation = road_spot
        adjacent = []

        for settlement, owner_id in self.all_settlements.items():
            if owner_id != player_id:  # ← Only your settlements
                continue

            settle_x, settle_y = settlement
            distance = ((road_x - settle_x) ** 2 + (road_y - settle_y) ** 2) ** 0.5

            if distance < 30:
                adjacent.append(settlement)

        return adjacent

    def get_adjacent_settlements_setup(self, road_spot, player_id,placed_settlement):
        """Return YOUR settlements adjacent to this road"""
        road_x, road_y, rotation = road_spot
        adjacent = []

        for settlement, owner_id in self.all_settlements.items():
            if owner_id != player_id:  # ← Only your settlements
                continue
            if settlement != placed_settlement:
                continue

            settle_x, settle_y = settlement
            distance = ((road_x - settle_x) ** 2 + (road_y - settle_y) ** 2) ** 0.5

            if distance < 30:
                adjacent.append(settlement)

        return adjacent

    def get_adjacent_roads(self, settlement_spot, player_id):
        """Return YOUR roads adjacent to this settlement"""
        settle_x, settle_y = settlement_spot
        adjacent = []

        for road, owner_id in self.all_roads.items():
            if owner_id != player_id:  # ← Only your roads
                continue

            road_x, road_y, rotation = road
            distance = ((settle_x - road_x) ** 2 + (settle_y - road_y) ** 2) ** 0.5

            if distance < 30:
                adjacent.append(road)

        return adjacent




if __name__ == "__main__":
    board = Board(font=None)

    print("First 10 road spots:")
    for i, spot in enumerate(board.board_road_spots[:10]):
        print(f"  {i}: {spot}")

    print("\nFirst 5 tiles:")
    for i, tile in enumerate(board.board_data[:5]):
        print(f"  Tile {i}: x={tile['x']}, y={tile['y']}")