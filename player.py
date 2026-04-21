class Player:
    def __init__(self, player_id, name, color):
        self.player_id = player_id
        self.name = name
        self.color = color

        # Resources
        self.resources = {
            "wood": 0,
            "wheat": 0,
            "ore": 0,
            "brick": 0,
            "sheep": 0
        }

        # Settlements and roads
        self.settlements = []  # List of tile positions
        self.roads = []  # List of edge positions
        self.cities = []  # List of upgraded settlements

        # Score
        self.victory_points = 0

    def add_resource(self, resource, amount):
        self.resources[resource] += amount

    def remove_resource(self, resource, amount):
        if self.resources[resource] >= amount:
            self.resources[resource] -= amount
            return True
        return False

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