Phase	What	Why
1 ✅	Board renders on all computers	Foundation
2	Player objects + turn system	Core structure
4	Game setup: starting settlements + roads	Players positioned before anything happens
     Player receives updated board data (settlements/roads from previous turns)
     Valid settlement spots are calculated and visible
     Player clicks on a settlement spot
     Client sends placement to server
     Server places it, updates board.all_settlements
     Server broadcasts complete state to all clients
     All clients update their board.all_settlements
     Player clicks on a road spot
     Client sends placement to server
     Server places it, updates board.all_roads
     Server broadcasts complete state to all clients
     All clients update their board.all_roads
     Next player's turn starts
6	Settlements/roads placement (mid-game)	Now placement mechanics work
3	Dice roll + resource distribution	Resources flow to placed settlements
5	Trading system	Players can trade
5.5 victory points 
7	Polish UI/UX	Professional
8	Art 	Eye candy
8.5 cities 
9	Robber	Stretch goal
9.5 limited amount of buildings 
9.75 animations 
10	Dev cards	Stretch goal







'''if player_state == "collecting_resources" and game_phase == "gameplay":
        # noinspection PyUnboundLocalVariable
        for tile in board.get_tiles_by_number(roll):'''

                if first_turn_tick:
                    player_state = "roll"
                    first_turn_tick = False











