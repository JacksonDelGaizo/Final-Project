# a test file so I can start the game quickly
#5/5/26
__author__ = "jackson del gaizo"


import subprocess
import time

#subprocess.Popen(["python", "server.py"])
time.sleep(1)  # Give server time to start

for i in range(4):
    subprocess.Popen(["python", "main.py"])
    time.sleep(0.2)