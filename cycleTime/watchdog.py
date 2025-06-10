import os
import time

while True:
    exit_code = os.system("python /app/Main.py")
    print(f"Process exited with code {exit_code}. Restarting in 5 seconds...")
    time.sleep(5)
