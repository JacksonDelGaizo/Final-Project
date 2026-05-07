# Catan

## Setup

Make sure you have all the files in a PyCharm project. Go into `main.py` and `server.py` and check that you see this code:

```python
server_socket.connect(("localhost", 6068))
```

Make sure it isn't going to try to connect to a different IP address. For grading this project, host everything locally.

## Running the Game

Go into your terminal and type:

```bash
python test.py
```

This will run the server and all four players on your computer. Each pygame window is a separate player.

## How to Play

**Setup Phase:** Each player places one settlement and a road connecting it until each player has placed two.

**Gameplay:**

- Accumulate resources by rolling the dice. When any player rolls a certain number, settlements on that tile will reward their player with one of that specific resource type. If the settlement is upgraded, it will reward two.
- Trade with other players for resources you don't need. Click the trade button, send your desired trade, then all other players must answer the trade. The server will make the trade with someone who accepted.
- Build roads, new settlements, and upgraded settlements using the other buttons. Keep in mind settlements can't be placed right next to each other.
- Accumulate victory points by building and upgrading settlements. When you get ten, you win the game.