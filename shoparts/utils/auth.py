from config import PASSWORD
import os
import time
import getpass

def login():
    while True:
        p = getpass.getpass("Enter the Password: ")
        if p == PASSWORD:
            return True
        print("Incorrect password. Try again.")
        time.sleep(2)
        os.system('cls' if os.name == 'nt' else 'clear')