import pygame
import json
import socket
from board import Board
from constants import *
import time
counter = 0
first_turn_tick = True
resources = {}

pygame.init()
pygame.mixer.init()
tile_number_font = pygame.font.SysFont('muktamahee', 20)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))

running = True

# load images
dice_button=pygame.image.load("images/dice.png")
end_turn_button=pygame.image.load("images/end_turn.png")
road_button=pygame.image.load("images/road.png")
settlement_button=pygame.image.load("images/settlement.png")
end_turn_wait_button=pygame.image.load("images/wait.png")

dice_button = pygame.transform.scale(dice_button, (50, 50))
end_turn_button = pygame.transform.scale(end_turn_button, (50, 50))
road_button = pygame.transform.scale(road_button, (50, 50))
settlement_button = pygame.transform.scale(settlement_button, (50, 50))
end_turn_wait_button = pygame.transform.scale(end_turn_wait_button, (50, 50))


dice_rect = dice_button.get_rect()
end_turn_rect = end_turn_button.get_rect()
road_rect = road_button.get_rect()
settlement_rect = settlement_button.get_rect()
end_turn_wait_rect = end_turn_wait_button.get_rect()

dice_rect.topleft = (800,700)
end_turn_rect.topleft = (1100,700)
road_rect.topleft = (900,700)
settlement_rect.topleft = (1000,700)
end_turn_wait_rect.topleft = (1100,700)

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
player_valid_spots = board.get_valid_gameplay_settlement_spots(player_id)

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
            if game_phase == "gameplay" and first_turn_tick and current_player == player_id:
                player_state = "roll"
                first_turn_tick = False
            roll = data.get("roll")
            if roll is not None:
                print('roll', roll)
            resources = data.get("resources", {})
            if resources is not None:
                # Update resources
                player_resources = resources
            print(f"Game phase: {game_phase}, Current player: {current_player}, player state: {player_state}")
            valid_spots = board.get_valid_settlement_spots()
            player_valid_spots = board.get_valid_gameplay_settlement_spots(player_id)
    except BlockingIOError:
        #print("eror")
        pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_spot = event.pos
            # Only process placement if it's your turn in setup
            if player_id == current_player and game_phase == "setup":


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
            if player_id == current_player and game_phase == "gameplay":

                if player_state == "roll":
                    if dice_rect.colliderect(clicked_spot):
                        #TODO when making ui check if player clicks dice and place dice roll sound
                        request = json.dumps({"action": "roll_dice"})
                        server_socket.send(request.encode())
                        print ("sent")
                        player_state = None
                        print (player_state)
                else:
                    if settlement_rect.colliderect(clicked_spot):
                        if player_state == "placing_settlement":
                            player_state = None
                        else:
                            player_state = "placing_settlement"
                    if road_rect.colliderect(clicked_spot):
                        if player_state == "placing_road":
                            player_state = None
                        else:
                            player_state = "placing_road"
                    if end_turn_rect.colliderect(clicked_spot):
                        request = json.dumps({"action": "end_turn"})
                        server_socket.send(request.encode())
                    if player_state == "placing_settlement":
                        for spot in player_valid_spots:
                            distance = ((clicked_spot[0] - spot[0]) ** 2 + (clicked_spot[1] - spot[1]) ** 2) ** 0.5
                            if distance < 20:
                                if resources["wood"] >= 1 and resources["brick"] >= 1 and resources["wheat"] >= 1 and resources["sheep"] >= 1:
                                    adjacent = board.get_adjacent_roads(spot, player_id)
                                    if adjacent:
                                        request = json.dumps({"action": "place_settlement_gameplay", "spot": spot})
                                        placed_settlement = spot
                                        server_socket.send(request.encode())

                    if player_state == "placing_road":
                        for road_spot in board.get_valid_road_spots():
                            road_x, road_y, rotation = road_spot
                            distance = ((clicked_spot[0] - road_x) ** 2 + (clicked_spot[1] - road_y) ** 2) ** 0.5
                            if distance < 20:
                                if resources["wood"] >= 1 and resources["brick"] >= 1:
                                    adjacent = board.get_adjacent_settlements(road_spot, player_id)
                                    if not adjacent:
                                        adjacent = board.get_adjacent_roads(road_spot, player_id)
                                    if adjacent:
                                        request = json.dumps({"action": "place_road_gameplay", "spot": road_spot})
                                        print(f"sending {request}")
                                        server_socket.send(request.encode())



                    #TODO all of the other turn actions that player can pressbutton each one doesn't need a player_state you can build and trade in any order


    if player_state == "ending_turn" and game_phase == "setup" and player_id == current_player:
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
    #  change game_phase == setup to player_state = placing settlement so we can build stuff in gameplay
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
    if player_id == current_player and game_phase == "gameplay":
        if player_state == "placing_settlement":
            for spot in player_valid_spots:
                pygame.draw.circle(screen, (0, 255, 0), spot, 10)  # Green circles
        elif player_state == "placing_road":
            for road_spot in board.get_valid_road_spots():
                if board.get_adjacent_settlements(road_spot,player_id):
                    road_x, road_y, rotation = road_spot
                    # Draw road lines based on rotation
                    if rotation == "horizontal":
                        pygame.draw.line(screen, (255, 255, 0), (road_x - 15, road_y), (road_x + 15, road_y), 5)  # Yellow
                    else:
                        pygame.draw.line(screen, (255, 255, 0), (road_x, road_y - 15), (road_x, road_y + 15), 5)  # Yellow
        else:
            pass
    # Always show placed settlements and roads
    colors = {0: (255, 0, 0), 1: (0, 0, 255), 2: (255, 255, 255), 3: (255, 165, 0)}
# draw settlements on board
    for settlement, owner_id in board.all_settlements.items():
        pygame.draw.circle(screen, colors[owner_id], settlement, 15)
# draw roads on board
    for road, owner_id in board.all_roads.items():
        road_x, road_y, rotation = road
        if rotation == "horizontal":
            pygame.draw.line(screen, colors[owner_id], (road_x - 15, road_y), (road_x + 15, road_y), 5)  # Brown
        else:
            pygame.draw.line(screen, colors[owner_id], (road_x, road_y - 15), (road_x, road_y + 15), 5)  # Brown
  #draw buttons
    screen.blit(road_button, road_rect)
    screen.blit(settlement_button, settlement_rect)
    if player_state == "roll":
        dice_button.set_alpha(255)
    else:
        dice_button.set_alpha(128)
    screen.blit(dice_button, dice_rect)
    if current_player == player_id:
        screen.blit(end_turn_button, end_turn_rect)
    else:
        screen.blit(end_turn_wait_button, end_turn_wait_rect)

# TODO draw cities on board

    pygame.display.flip()

pygame.quit()