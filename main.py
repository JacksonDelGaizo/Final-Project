import pygame
import json
import socket
from board import Board
from constants import *
import time
counter = 0

pygame.init()
tile_number_font = pygame.font.SysFont('muktamahee', 20)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))

running = True

# CONNECT TO SERVER AND GET BOARD DATA
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(("localhost", 6067))

    # Receive combined data
    message = server_socket.recv(4096).decode()
    data = json.loads(message)

    player_id = data["player_id"]
    board_data = data["board_data"]

    board = Board(board_data=board_data, font=tile_number_font)
    server_socket.setblocking(False)

except Exception as e:
    print(f"Could not connect to server: {e}")
    exit()

# Game state
game_phase = "setup"
current_player = 0
player_state = "placing_settlement"
valid_spots = board.get_valid_settlement_spots()

all_players_connected = False

# Wait for all players to connect
print("Waiting for all players to connect...")
while not all_players_connected:
    try:
        message = server_socket.recv(4096).decode()
        if message:
            data = json.loads(message)
            all_players_connected = data.get("all_players_connected", False)
            if all_players_connected:
                print("All players connected! Game starting...")
    except BlockingIOError:
        time.sleep(0.1)  # Don't spin the CPUwe

while running:
    try:
        message = server_socket.recv(4096).decode()
        #print(message)
        if message:
            data = json.loads(message)
            settlements_list = data.get("all_settlements", [])
            roads_list = data.get("all_roads", [])
            board.all_settlements = {tuple(spot): player_id for spot, player_id in settlements_list}
            board.all_roads = {tuple(spot): player_id for spot, player_id in roads_list}
            current_player = data.get("current_player", 0)
            game_phase = data.get("game_phase", "setup")
            roll = data.get("roll", 0)
            print(f"Game phase: {game_phase}, Current player: {current_player}, player state: {player_state}")
            valid_spots = board.get_valid_settlement_spots()
    except BlockingIOError:
        #print("eror")
        pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Only process placement if it's your turn in setup
            if player_id == current_player and game_phase == "setup":
                mouse_x, mouse_y = pygame.mouse.get_pos()
                clicked_spot = (mouse_x, mouse_y)

                if player_state == "placing_settlement":
                    for spot in valid_spots:
                        distance = ((clicked_spot[0] - spot[0]) ** 2 + (clicked_spot[1] - spot[1]) ** 2) ** 0.5
                        if distance < 20:
                            request = json.dumps({"action": "place_settlement", "spot": spot})
                            placed_settlement = spot
                            print(request)
                            server_socket.send(request.encode())
                            player_state = "placing_road"
                            break

                elif player_state == "placing_road":
                    for road_spot in board.get_valid_road_spots():
                        road_x, road_y, rotation = road_spot
                        distance = ((clicked_spot[0] - road_x) ** 2 + (clicked_spot[1] - road_y) ** 2) ** 0.5
                        if distance < 20:
                            # Check if adjacent to a settlement
                            adjacent = board.get_adjacent_settlements_setup(road_spot, player_id,placed_settlement)
                            if adjacent:
                                request = json.dumps({"action": "place_road", "spot": road_spot})
                                print(f"sending {request}")
                                server_socket.send(request.encode())
                                player_state = "ending_turn"
                                break
        elif player_state == "ending_turn" and game_phase == "setup" and player_id == current_player:
            counter += 1
            print (counter)
            if counter == 25:
                print ("ENDING TURN")
                request = json.dumps({"action": "end_turn"})
                server_socket.send(request.encode())
                player_state = "placing_settlement"
                placed_settlement = None
                counter = 0



    screen.fill((65, 105, 225))
    board.tiles.draw(screen)

    # Only show placement dots if it's your turn in setup
    if player_id == current_player and game_phase == "setup":
        if player_state == "placing_settlement":
            for spot in valid_spots:
                pygame.draw.circle(screen, (0, 255, 0), spot, 10)  # Green circles
        elif player_state == "placing_road":
            for road_spot in board.get_valid_road_spots():
                if board.get_adjacent_settlements_setup(road_spot,player_id,placed_settlement):
                    road_x, road_y, rotation = road_spot
                    # Draw road lines based on rotation
                    if rotation == "horizontal":
                        pygame.draw.line(screen, (255, 255, 0), (road_x - 15, road_y), (road_x + 15, road_y), 5)  # Yellow
                    else:
                        pygame.draw.line(screen, (255, 255, 0), (road_x, road_y - 15), (road_x, road_y + 15), 5)  # Yellow

    # Always show placed settlements and roads
    colors = {0: (255, 0, 0), 1: (0, 0, 255), 2: (255, 255, 255), 3: (255, 165, 0)}

    for settlement, owner_id in board.all_settlements.items():
        pygame.draw.circle(screen, colors[owner_id], settlement, 15)

    for road, owner_id in board.all_roads.items():
        road_x, road_y, rotation = road
        if rotation == "horizontal":
            pygame.draw.line(screen, colors[owner_id], (road_x - 15, road_y), (road_x + 15, road_y), 5)  # Brown
        else:
            pygame.draw.line(screen, colors[owner_id], (road_x, road_y - 15), (road_x, road_y + 15), 5)  # Brown

    pygame.display.flip()

pygame.quit()