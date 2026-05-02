import socket
import json
import random
from board import Board

from player import Player
import select
#import time


class GameServer:
    def __init__(self, num_players=4):
        self.players = []
        self.current_player = 0
        self.board = Board(None)  # Server doesn't need font
        self.setup_order = list(range(num_players))
        random.shuffle(self.setup_order)
        self.setup_index = 0  # Track position in setup_order

        # Create players
        colors = ["red", "blue", "white", "orange"]
        for i in range(num_players):
            player = Player(i, f"Player {i + 1}", colors[i])
            self.players.append(player)

        # Game state
        self.game_started = False
        self.current_phase = "setup"  # roll, trade, build, end_turn

    def setup_game(self):
        pass

    def place_settlement(self, settlement_spot, player_id):
        """Place a settlement on the board"""
        self.board.all_settlements[settlement_spot] = player_id
        self.players[player_id].place_settlement(settlement_spot)
    def place_settlement_gameplay(self, settlement_spot, player_id):

        self.board.all_settlements[settlement_spot] = player_id
        self.players[player_id].place_settlement(settlement_spot)
        self.players[player_id].remove_resource("wood", 1)
        self.players[player_id].remove_resource("brick", 1)
        self.players[player_id].remove_resource("wheat", 1)
        self.players[player_id].remove_resource("sheep", 1)

    def place_road(self, road_spot, player_id):
        """Place a road on the board"""
        self.board.all_roads[road_spot] = player_id
        self.players[player_id].place_road(road_spot)
    def place_road_gameplay(self, road_spot, player_id):
        """Place a road on the board"""
        self.board.all_roads[road_spot] = player_id
        self.players[player_id].place_road(road_spot)
        self.players[player_id].remove_resource("wood", 1)
        self.players[player_id].remove_resource("brick", 1)

    def roll_dice(self):
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        return total

    def gather_resource(self, player_id, number):
        """Give resources to a player based on dice roll"""
        for tile in self.board.board_data:
            if tile["number"] != number:
                continue
            if tile["resource"] == "desert":
                continue

            tile_center_x = tile["x"] + 50
            tile_center_y = tile["y"] + 50

            # Check all settlements
            for settlement, owner_id in self.board.all_settlements.items():
                if owner_id != player_id:
                    continue

                settle_x, settle_y = settlement
                distance = ((settle_x - tile_center_x) ** 2 + (settle_y - tile_center_y) ** 2) ** 0.5

                if distance < 80:  # Close enough to be adjacent
                    self.players[player_id].add_resource(tile["resource"], 1)

    def trade(self):
        pass

    def build(self):
        pass

    def next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)
    def end_turn(self):
        self.next_turn()
        self.current_phase = "roll_dice"

    def end_turn_in_setup(self):
        self.setup_index += 1

        # Check if setup is complete (8 turns total: 2 per player)
        if self.setup_index >= 8:
            self.current_phase = "gameplay"
            self.current_player = 0
            return

        # Simple: just cycle through players 0→1→2→3→0→1→2→3
        self.current_player = self.setup_index % 4

    def check_winner(self):
        for player in self.players:
            if player.victory_points >= 10:
                return player
        return None


# Create server and game
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("localhost", 6067))
server_socket.listen(5)

print("Server listening on port 6067...")

game = GameServer(num_players=4)

# Keep track of all connected clients
connected_clients = []
client_to_player = {}
client_num = 0

while client_num < 4:
    print(client_num)
    client_socket, address = server_socket.accept()
    client_to_player[client_socket] = client_num
    print(f"Player {client_num} connected: {address}")

    # Send initial data
    combined_data = {
        "player_id": client_num,
        "board_data": game.board.board_data
    }
    combined_json = json.dumps(combined_data)
    client_socket.send(combined_json.encode())

    connected_clients.append(client_socket)
    client_num += 1

print("All players connected! Game starting...")



# Send "game starting" message to all clients
for client in connected_clients:
    response = json.dumps({"all_players_connected": True})
    client.send(response.encode())

# MAIN GAME LOOP
while True:
        # Use select to check which sockets have data
    readable, _, _ = select.select(connected_clients, [], [], 0.1)
    # Listen for messages from any client
    for client_socket in readable:
        try:
            message = client_socket.recv(4096).decode()
            #print(message)
            if message:
                player_id = client_to_player[client_socket]
                command = json.loads(message)
                print(f"Received command: {command}")

                if command["action"] == "roll_dice":
                    result = game.roll_dice()
                    print (result)

                    for player in game.players:
                        game.gather_resource(player.player_id, result)
                    settlements_list = [[list(k), v] for k, v in game.board.all_settlements.items()]
                    roads_list = [[list(k), v] for k, v in game.board.all_roads.items()]

                    for sock, pid in client_to_player.items():
                        response = json.dumps({
                            "resources": game.players[pid].resources,
                            "roll": result,
                            "all_settlements": settlements_list,
                            "all_roads": roads_list,
                            "current_player": game.current_player,
                            "game_phase": game.current_phase

                        })
                        sock.send(response.encode())
                        print(response)

                if command["action"] == "place_settlement":
                    settlement_spot = tuple(command["spot"])

                    game.place_settlement(settlement_spot, player_id)

                    # Convert dicts to JSON
                    settlements_list = [[list(k), v] for k, v in game.board.all_settlements.items()]
                    roads_list = [[list(k), v] for k, v in game.board.all_roads.items()]

                    # Broadcast updated state

                    response = json.dumps({
                        "all_settlements": settlements_list,
                        "all_roads": roads_list,
                        "current_player": game.current_player,
                        "game_phase": game.current_phase
                    })

                    for client in connected_clients:
                        client.send(response.encode())

                if command["action"] == "place_road":
                    road_spot = tuple(command["spot"])
                    game.place_road(road_spot, player_id)
                    # Convert dicts to JSON
                    settlements_list = [[list(k), v] for k, v in game.board.all_settlements.items()]
                    roads_list = [[list(k), v] for k, v in game.board.all_roads.items()]

                    # Broadcast updated state
                    response = json.dumps({
                        "all_settlements": settlements_list,
                        "all_roads": roads_list,
                        "current_player": game.current_player,
                        "game_phase": game.current_phase
                    })

                    for client in connected_clients:
                        client.send(response.encode())

                if command["action"] == "end_turn":
                    if game.current_phase == "setup":
                        game.end_turn_in_setup()
                    else:
                        game.end_turn()
                    # Convert dicts to JSON
                    settlements_list = [[list(k), v] for k, v in game.board.all_settlements.items()]
                    roads_list = [[list(k), v] for k, v in game.board.all_roads.items()]

                    # Broadcast updated state
                    response = json.dumps({
                        "all_settlements": settlements_list,
                        "all_roads": roads_list,
                        "current_player": game.current_player,
                        "game_phase": game.current_phase
                    })
                    for client in connected_clients:
                        client.send(response.encode())

                if command["action"] == "place_settlement_gameplay":
                    settlement_spot = tuple(command["spot"])

                    game.place_settlement_gameplay(settlement_spot, player_id)

                    # Convert dicts to JSON
                    settlements_list = [[list(k), v] for k, v in game.board.all_settlements.items()]
                    roads_list = [[list(k), v] for k, v in game.board.all_roads.items()]

                    # Broadcast updated state
                    for sock, pid in client_to_player.items():
                        response = json.dumps({
                            "all_settlements": settlements_list,
                            "all_roads": roads_list,
                            "current_player": game.current_player,
                            "game_phase": game.current_phase,
                            "resources": game.players[pid].resources
                        })
                        sock.send(response.encode())
                if command["action"] == "place_road_gameplay":
                    road_spot = tuple(command["spot"])

                    game.place_road_gameplay(road_spot, player_id)

                    # Convert dicts to JSON
                    settlements_list = [[list(k), v] for k, v in game.board.all_settlements.items()]
                    roads_list = [[list(k), v] for k, v in game.board.all_roads.items()]

                    # Broadcast updated state
                    for sock, pid in client_to_player.items():
                        response = json.dumps({
                            "all_settlements": settlements_list,
                            "all_roads": roads_list,
                            "current_player": game.current_player,
                            "game_phase": game.current_phase,
                            "resources": game.players[pid].resources
                        })
                        sock.send(response.encode())


        except Exception as e:
            print(f"Error: {e}")