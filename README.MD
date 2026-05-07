# Game Setup and Gameplay Guide

## Setup Instructions

Follow these steps to set up and run the game:

1. **Prepare the Project Files:** Ensure all project files are organized in a PyCharm project directory. By the way 

2. **Verify Connection Settings:** Open both `main.py` and `server.py` and verify that the server connection uses:
   ```
   server_socket.connect(("localhost", 6068))
   ```
   Ensure the connection is set to `localhost` and not configured to connect to a different IP address. For grading purposes, everything should be hosted locally.

3. **Run the Test Suite:** Open your terminal and run:
   ```bash
   python test.py
   ```
   This will start the server and launch all four players on your computer. Each Pygame window represents a separate player.

## Gameplay

### Phase 1: Setup Phase

Each player places one settlement and a road connecting to it. This continues until each player has placed two settlements and two roads.

### Phase 2: Main Gameplay

**Resource Accumulation:** Roll the dice to accumulate resources. When any player rolls a certain number, settlements positioned on tiles matching that number will reward the player with one of that resource type. Upgraded settlements reward two resources instead of one.

**Trading:** Trade resources with other players. Click the trade button, send your desired trade offer, and all other players must respond. The server will execute the trade with a player who accepts your offer.

**Building:** Use the available buttons to build roads, new settlements, and upgraded settlements. Keep in mind that settlements cannot be placed directly next to each other.

**Victory Condition:** Accumulate victory points by building and upgrading settlements. The first player to reach 10 victory points wins the game.

