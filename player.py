#file for player class which stores all necessary information for a player, the game class makes and stores for of them
#5/5/26
__author__ = "jackson del gaizo"

class Player:
    def __init__(self, player_id, name, color):
        self.player_id = player_id
        self.name = name
        self.color = color

        # Resources
        self.resources = {
            "brick": 0,
            "ore": 0,
            "sheep": 0,
            "wheat": 0,
            "wood": 0
        }

        # Settlements and roads
        self.settlements = []  # List of tile positions
        self.roads = []  # List of edge positions
        self.cities = []  # List of upgraded settlements

        # Score
        self.victory_points = 2

    def add_resource(self, resource, amount):
        self.resources[resource] += amount

    def remove_resource(self, resource, amount):
        if self.resources[resource] >= amount:
            self.resources[resource] -= amount
            return True
        return False

    def remove_resource2(self, resource, amount):
        self.resources[resource] -= amount

    def place_settlement(self, settlement_id):
        self.settlements.append(settlement_id)

    def place_road(self, road_id):
        self.roads.append(road_id)

    def vp(self,amount):
        self.victory_points += amount

    def upgrade_settlement(self, settlement_id):
        if settlement_id in self.settlements:
            self.settlements.remove(settlement_id)
            self.cities.append(settlement_id)