#This is the client side of the game. This is what the user interacts with to send commands to the server main.py  visually displays the game
#5/5/26
__author__ = "jackson del gaizo"


#mode = "test"
#import section
import pygame
#json for socket
import json
import socket
from board import Board
from constants import *
import time
counter = 0
has_required_materials_for_trade=False
settlement_peices=3
city_peices=4
road_peices=13
first_turn_tick = True
resources = {}
player_resources = {}
roll = ''
win=False
# two dictioraires for proposing trade
give = {
            "brick": 0,
            "ore": 0,
            "sheep": 0,
            "wheat": 0,
            "wood": 0
        }
get = {
            "brick": 0,
            "ore": 0,
            "sheep": 0,
            "wheat": 0,
            "wood": 0
        }
# resets give and get when trade is complete
def reset():
    global give,get
    give = {
        "brick": 0,
        "ore": 0,
        "sheep": 0,
        "wheat": 0,
        "wood": 0
    }
    get = {
        "brick": 0,
        "ore": 0,
        "sheep": 0,
        "wheat": 0,
        "wood": 0
    }


pygame.init()
pygame.mixer.init()
# gameplay sounds
bell=pygame.mixer.Sound('sounds/bell.wav')
click=pygame.mixer.Sound('sounds/click.wav')
build=pygame.mixer.Sound('sounds/build .wav')
roll_dice=pygame.mixer.Sound('sounds/dice_roll.wav')
# fonts
tile_number_font = pygame.font.SysFont('muktamahee', 20)
font = pygame.font.SysFont('montserrat', 24)
#screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))

running = True

# load images
city_button = pygame.image.load("images/city_button.png")
info=pygame.image.load("images/info.png")
dice_button=pygame.image.load("images/dice.png")
end_turn_button=pygame.image.load("images/end_turn.png")
road_button=pygame.image.load("images/road.png")
settlement_button=pygame.image.load("images/settlement.png")
end_turn_wait_button=pygame.image.load("images/wait.png")
trade_button = pygame.image.load("images/trade.png")
brick=pygame.image.load("images/brick.png")
ore=pygame.image.load("images/ore.png")
sheep=pygame.image.load("images/sheep.png")
wheat=pygame.image.load("images/wheat.png")
wood=pygame.image.load("images/wood.png")
confirm=pygame.image.load("images/confirm.png")
reset = pygame.image.load("images/reset.png")
# make the ui
dice_button = pygame.transform.scale(dice_button, (50, 50))
end_turn_button = pygame.transform.scale(end_turn_button, (50, 50))
road_button = pygame.transform.scale(road_button, (50, 50))
settlement_button = pygame.transform.scale(settlement_button, (50, 50))
end_turn_wait_button = pygame.transform.scale(end_turn_wait_button, (50, 50))
trade_button = pygame.transform.scale(trade_button, (50, 50))
city_button = pygame.transform.scale(city_button, (50, 50))
brick = pygame.transform.scale(brick, (25, 25))
ore = pygame.transform.scale(ore, (25, 25))
sheep = pygame.transform.scale(sheep, (25, 25))
wheat = pygame.transform.scale(wheat, (25, 25))
wood = pygame.transform.scale(wood, (25, 25))
confirm=pygame.transform.scale(confirm, (150, 30))
reset = pygame.transform.scale(reset, (150, 30))
info = pygame.transform.scale(info, (200, 200))


dice_rect = dice_button.get_rect()
info_rect = info.get_rect()
end_turn_rect = end_turn_button.get_rect()
road_rect = road_button.get_rect()
settlement_rect = settlement_button.get_rect()
end_turn_wait_rect = end_turn_wait_button.get_rect()
trade_rect = trade_button.get_rect()
brick_rect = brick.get_rect()
ore_rect = ore.get_rect()
sheep_rect = sheep.get_rect()
wheat_rect = wheat.get_rect()
wood_rect = wood.get_rect()
city_rect = city_button.get_rect()
give_brick_rect = brick.get_rect()
give_ore_rect = ore.get_rect()
give_sheep_rect = sheep.get_rect()
give_wheat_rect = wheat.get_rect()
give_wood_rect = wood.get_rect()
get_brick_rect = brick.get_rect()
get_ore_rect = ore.get_rect()
get_sheep_rect = sheep.get_rect()
get_wheat_rect = wheat.get_rect()
get_wood_rect = wood.get_rect()
confirm_rect = confirm.get_rect()
reset_rect = reset.get_rect()
# position the ui
trade_rect.topleft = (700,700)
city_rect.topleft = (600,700)
info_rect.topleft = (900,200)
dice_rect.topleft = (800,700)
end_turn_rect.topleft = (1100,700)
road_rect.topleft = (900,700)
settlement_rect.topleft = (1000,700)
end_turn_wait_rect.topleft = (1100,700)
brick_rect.topleft = (70,600)
ore_rect.topleft = (70,630)
sheep_rect.topleft = (70,660)
wheat_rect.topleft = (70,690)
wood_rect.topleft = (70,720)
give_brick_rect.topleft = (70,50)
give_ore_rect.topleft = (70,80)
give_sheep_rect.topleft = (70,110)
give_wheat_rect.topleft = (70,140)
give_wood_rect.topleft = (70,170)
get_brick_rect.topleft = (250,50)
get_ore_rect.topleft = (250,80)
get_sheep_rect.topleft = (250,110)
get_wheat_rect.topleft = (250,140)
get_wood_rect.topleft = (250,170)
confirm_rect.topleft= (70,200)
reset_rect.topleft= (70,240)



#192.168.4.35
# connect player to server.py using socket
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # localhost means it isn't online are is for test
    server_socket.connect(("localhost", 6069))

    # Receive the randomly generated board
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
        time.sleep(0.1)  # Don't spin the CPU

while running:
    try:
        message = server_socket.recv(4096).decode()
        #print(message)
        if message:
            data = json.loads(message)
            settlements_list = data.get("all_settlements", [])
            roads_list = data.get("all_roads", [])
            city_list = data.get("all_cities", [])
            board.all_settlements = {tuple(spot): player_id for spot, player_id in settlements_list}
            board.all_roads = {tuple(spot): player_id for spot, player_id in roads_list}
            board.all_cities = {tuple(spot): player_id for spot, player_id in city_list}
            current_player = data.get("current_player", 0)
            game_phase = data.get("game_phase", "setup")
            if game_phase == "gameplay" and first_turn_tick and current_player == player_id:
                player_state = "roll"
                bell.play()
                first_turn_tick = False

            roll = data.get("roll")
            if roll is not None:
                print('roll', roll)
            resources = data.get("resources", {})
            if resources is not None:
                # Update resources
                player_resources = resources
            new_get=data.get("get")
            new_give=data.get("give")
            if new_give is not None:
                player_state = "accepting_trade"
                give=new_give
                get=new_get
                #check materials
                for material, count in give.items():
                    if count == 0:
                        continue
                    if player_resources[material] < count:
                        has_required_materials_for_trade = False
                        break
                    else:
                        has_required_materials_for_trade = True
                print(f"has_required_materials_for_trade: {has_required_materials_for_trade}")



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
            click.play()
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
                            build.play()
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
                                build.play()
                                player_state = "ending_turn"
                                break
            if player_id == current_player and game_phase == "gameplay":

                if player_state == "roll":
                    if dice_rect.collidepoint(clicked_spot):
                        roll_dice.play()
                        request = json.dumps({"action": "roll_dice"})
                        server_socket.send(request.encode())
                        print ("sent")
                        player_state = None
                        print (player_state)
                else:
                    if settlement_rect.collidepoint(clicked_spot):
                        if player_state == "placing_settlement":
                            player_state = None
                        else:
                            player_state = "placing_settlement"
                    if road_rect.collidepoint(clicked_spot):
                        if player_state == "placing_road":
                            player_state = None
                        else:
                            player_state = "placing_road"
                    if end_turn_rect.collidepoint(clicked_spot):
                        request = json.dumps({"action": "end_turn"})
                        server_socket.send(request.encode())
                        first_turn_tick = True
                    if trade_rect.collidepoint(clicked_spot):
                        if player_state == "trading":
                            player_state = None
                        else:
                            player_state = "trading"
                    if city_rect.collidepoint(clicked_spot):
                        if player_state == "placing_city":
                            player_state = None
                        else:
                            player_state = "placing_city"
                    if player_state == "placing_settlement":
                        for spot in player_valid_spots:
                            distance = ((clicked_spot[0] - spot[0]) ** 2 + (clicked_spot[1] - spot[1]) ** 2) ** 0.5
                            if distance < 20:
                                if player_resources["wood"] >= 1 and player_resources["brick"] >= 1 and player_resources["wheat"] >= 1 and player_resources["sheep"] >= 1:
                                    adjacent = board.get_adjacent_roads(spot, player_id)
                                    if adjacent:
                                        if settlement_peices > 0:
                                            request = json.dumps({"action": "place_settlement_gameplay", "spot": spot})
                                            placed_settlement = spot
                                            server_socket.send(request.encode())
                                            settlement_peices -= 1
                                            build.play()

                    if player_state == "placing_road":
                        for road_spot in board.get_valid_road_spots():
                            road_x, road_y, rotation = road_spot
                            distance = ((clicked_spot[0] - road_x) ** 2 + (clicked_spot[1] - road_y) ** 2) ** 0.5
                            if distance < 20:
                                if player_resources["wood"] >= 1 and player_resources["brick"] >= 1:
                                    adjacent = board.get_adjacent_settlements(road_spot, player_id)
                                    if not adjacent:
                                        adjacent = board.get_adjacent_roads_to_road(road_spot, player_id)
                                    if adjacent:
                                        if road_peices > 0:
                                            request = json.dumps({"action": "place_road_gameplay", "spot": road_spot})
                                            print(f"sending {request}")
                                            server_socket.send(request.encode())
                                            road_peices -= 1
                                            build.play()

                    if player_state == "trading":
                        if give_brick_rect.collidepoint(clicked_spot):
                            if player_resources["brick"] >= 1:
                                give["brick"] += 1
                        if give_ore_rect.collidepoint(clicked_spot):
                            if player_resources["ore"] >= 1:
                                give["ore"] += 1
                        if give_sheep_rect.collidepoint(clicked_spot):
                            if player_resources["sheep"] >= 1:
                                give["sheep"] += 1
                        if give_wheat_rect.collidepoint(clicked_spot):
                            if player_resources["wheat"] >= 1:
                                give["wheat"] += 1
                        if give_wood_rect.collidepoint(clicked_spot):
                            if player_resources["wood"] >= 1:
                                give["wood"] += 1
                        if get_brick_rect.collidepoint(clicked_spot):
                            get["brick"] += 1
                        if get_ore_rect.collidepoint(clicked_spot):
                            get["ore"] += 1
                        if get_sheep_rect.collidepoint(clicked_spot):
                            get["sheep"] += 1
                        if get_wheat_rect.collidepoint(clicked_spot):
                            get["wheat"] += 1
                        if get_wood_rect.collidepoint(clicked_spot):
                            get["wood"] += 1
                        if confirm_rect.collidepoint(clicked_spot):
                            request= json.dumps({"action": "propose_trade", "give": give, "get": get})
                            server_socket.send(request.encode())
                            player_state=None
                        if reset_rect.collidepoint(clicked_spot):
                            give = {
                                "brick": 0,
                                "ore": 0,
                                "sheep": 0,
                                "wheat": 0,
                                "wood": 0
                            }
                            get = {
                                "brick": 0,
                                "ore": 0,
                                "sheep": 0,
                                "wheat": 0,
                                "wood": 0
                            }

                    if player_state == "placing_city":
                        for city_spot in board.get_valid_city_spots(player_id):
                            city_x, city_y, owner_id = city_spot
                            distance = ((clicked_spot[0] - city_x) ** 2 + (clicked_spot[1] - city_y) ** 2) ** 0.5
                            if distance < 20:
                                if player_resources["wheat"] >= 2 and player_resources["ore"] >= 3:
                                    if city_peices > 0:
                                        request = json.dumps({"action": "place_city", "spot": city_spot})
                                        print(f"sending {request}")
                                        server_socket.send(request.encode())
                                        city_peices -= 1
                                        settlement_peices += 1
                                        build.play()





                    #TODO all of the other turn actions that player can pressbutton each one doesn't need a player_state you can build and trade in any order
            if player_state == "accepting_trade":
                if confirm_rect.collidepoint(clicked_spot):
                    if has_required_materials_for_trade:
                        request = json.dumps({"action": "answer_trade","decision":"accept","player_id": player_id})
                        server_socket.send(request.encode())
                        player_state = None
                if reset_rect.collidepoint(clicked_spot):
                    request = json.dumps({"action": "answer_trade","decision":"reject","player_id": player_id})
                    server_socket.send(request.encode())
                    player_state = None


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
    if game_phase == "game_over":
        if current_player==player_id:
            win=True
            running=False
        else:
            running=False








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

                elif board.get_adjacent_roads_to_road(road_spot,player_id):
                    road_x, road_y, rotation = road_spot
                    # Draw road lines based on rotation
                    if rotation == "horizontal":
                        pygame.draw.line(screen, (255, 255, 0), (road_x - 15, road_y), (road_x + 15, road_y),5)  # Yellow
                    else:
                        pygame.draw.line(screen, (255, 255, 0), (road_x, road_y - 15), (road_x, road_y + 15),5)  # Yellow
        elif player_state == "placing_city":
            for city_spot in board.get_valid_city_spots(player_id):
                city_x, city_y, owner_id = city_spot
                pygame.draw.circle(screen, (255, 215, 0), (city_x, city_y), 35)  # Gold

        else:
            pass
    # Always show placed settlements and roads
    colors = {0: (255, 0, 0), 1: (0, 0, 255), 2: (255, 255, 255), 3: (255, 165, 0)}
# draw settlements on board
    for settlement, owner_id in board.all_settlements.items():
        pygame.draw.circle(screen, colors[owner_id], settlement, 15)
    for city, owner_id in board.all_cities.items():
        pygame.draw.circle(screen, (0,0,0), city, 15,4)
# draw roads on board
    for road, owner_id in board.all_roads.items():
        road_x, road_y, rotation = road
        if rotation == "horizontal":
            pygame.draw.line(screen, colors[owner_id], (road_x - 15, road_y), (road_x + 15, road_y), 5)  # Brown
        else:
            pygame.draw.line(screen, colors[owner_id], (road_x, road_y - 15), (road_x, road_y + 15), 5)  # Brown
  #draw buttons
    if game_phase == "gameplay":
        if player_resources["wood"] >=1 and player_resources["brick"] >=1:
            road_button.set_alpha(255)
        else:
            road_button.set_alpha(128)
        if player_resources["wood"] >=1 and player_resources["brick"] >=1 and player_resources["wheat"] >=1 and player_resources["sheep"] >= 1:
            settlement_button.set_alpha(255)
        else:
            settlement_button.set_alpha(128)
        if player_resources["wheat"] >=2 and player_resources["ore"] >= 3:
            city_button.set_alpha(255)
        else:
            city_button.set_alpha(128)
    screen.blit(road_button, road_rect)
    screen.blit(info,info_rect)
    screen.blit(city_button,city_rect)
    screen.blit(settlement_button, settlement_rect)
    screen.blit(trade_button, trade_rect)
    if player_state == "roll":
        dice_button.set_alpha(255)
        settlement_button.set_alpha(128)
        road_button.set_alpha(128)
        end_turn_button.set_alpha(128)
        trade_button.set_alpha(128)
    else:
        dice_button.set_alpha(128)
        settlement_button.set_alpha(255)
        road_button.set_alpha(255)
        end_turn_button.set_alpha(255)
        trade_button.set_alpha(255)
    screen.blit(dice_button, dice_rect)
    if current_player == player_id:
        screen.blit(end_turn_button, end_turn_rect)
    else:
        screen.blit(end_turn_wait_button, end_turn_wait_rect)
    #draw resource count:
    screen.blit (brick,brick_rect)
    screen.blit (ore,ore_rect)
    screen.blit (sheep,sheep_rect)
    screen.blit (wheat,wheat_rect)
    screen.blit (wood,wood_rect)
    x=0
    for resource, amount in player_resources.items():
        text_surface = font.render(str(f":{amount}"), True, (0, 0, 0))
        text_x = 96
        text_y = 605+(30*x)
        screen.blit(text_surface, (text_x, text_y))
        x+=1
    if game_phase == "gameplay":
        text_surface = font.render(str(f"roll:{roll}"), True, (0, 0, 0))
        x_pos=800
        y_pos=670
        screen.blit(text_surface,(x_pos,y_pos))
        if settlement_peices == 0:
            text_surface = font.render(str(f"amount:{settlement_peices}"), True, (255, 0, 0))
        else:
            text_surface = font.render(str(f"amount:{settlement_peices}"), True, (0, 0, 0))
        x_pos=1000
        y_pos=670
        screen.blit(text_surface,(x_pos,y_pos))
        if road_peices == 0:
            text_surface = font.render(str(f"amount:{road_peices}"), True, (255, 0, 0))
        else:
            text_surface = font.render(str(f"amount:{road_peices}"), True, (0, 0, 0))
        x_pos=900
        y_pos=670
        screen.blit(text_surface,(x_pos,y_pos))
        if city_peices == 0:
            text_surface = font.render(str(f"amount:{city_peices}"), True, (255, 0, 0))
        else:
            text_surface = font.render(str(f"amount:{city_peices}"), True, (0, 0, 0))
        x_pos=600
        y_pos=670
        screen.blit(text_surface,(x_pos,y_pos))
    #render the trade screen.

    if player_state == "trading" or player_state == "accepting_trade":
        screen.blit(brick, get_brick_rect)
        screen.blit(ore, get_ore_rect)
        screen.blit(sheep, get_sheep_rect)
        screen.blit(wheat, get_wheat_rect)
        screen.blit(wood, get_wood_rect)
        screen.blit(brick, give_brick_rect)
        screen.blit(ore, give_ore_rect)
        screen.blit(sheep, give_sheep_rect)
        screen.blit(wheat, give_wheat_rect)
        screen.blit(wood, give_wood_rect)
        if player_state == "accepting_trade" and has_required_materials_for_trade == False:
            confirm.set_alpha(128)
        else:
            confirm.set_alpha(255)
        screen.blit(confirm, confirm_rect)
        screen.blit(reset, reset_rect)
        x = 0
        for resource, amount in give.items():

            text_surface = font.render(str(f":{amount}"), True, (0, 0, 0))
            text_x = 96
            text_y = 50+(30*x)
            screen.blit(text_surface, (text_x, text_y))
            x+=1
        x = 0
        for resource, amount in get.items():

            text_surface = font.render(str(f":{amount}"), True, (0, 0, 0))
            text_x = 276
            text_y = 50+(30*x)
            screen.blit(text_surface, (text_x, text_y))
            x+=1






# TODO draw cities on board

    pygame.display.flip()
overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
overlay.set_alpha(200)
overlay.fill((0, 0, 0))
screen.blit(overlay, (0, 0))
if win == True:
    game_over_text = font.render("You won", True, (0, 255, 0))
else:
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"winner is Player: {current_player+1}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
    screen.blit(score_text, score_rect)
text1 = font.render("press q to quit", True, (255, 0, 0))
game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
text_rect = text1.get_rect(center=(SCREEN_WIDTH // 2, 600))
screen.blit(game_over_text, game_over_rect)
screen.blit(text1, text_rect)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()






pygame.quit()