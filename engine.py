from __future__ import annotations
import sys
import time
import os
from functools import wraps
from typing import TYPE_CHECKING

# Import Player only for static type checking — avoids a circular import at runtime.
if TYPE_CHECKING:
    from entities import Player

# ANSI Color Codes natively supported by WSL
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

def clear_screen():
    """Clears the terminal screen for a clean UI."""
    print("\033[2J\033[H", end="")
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(delay = 0.01, color = Colors.RESET):
    """
    A custom decorator that prints the output of a function
    character by character to simulate a typewriter effect.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)
            if text:
                sys.stdout.write(color)
                for char in text:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(delay)
                print() # new line
        return wrapper
    return decorator

@typewriter(delay = 0.01)
def display_intro():
    return f"""{Colors.CYAN}
        /=========================================\\
        |      WELCOME TO THE DUNGEONS OF PPY     |
        \\=========================================/
        | You awaken in a dark, cold room.        |
        | The smell of damp stone fills the air.  |
        | You see a skeleton lying down on the    |
        | ground, once a human like you. Your need|
        | to get out is giving you severe anxiety.|
        |                                         |
        | You do not remember when or how you've  |
        | come this place. Last thing you remember|
        | is that you had to finish your python   |
        | project on the last day of submission . |
        |                                         |
        | Checking if the corpse has something    |
        | valuable would be intelligent to do     |
        | before you step out. You are taking     |
        | whatever you can while you still can.   |
        /=========================================\\
        | Your journey begins now...              |
        \\=========================================/

{Colors.RESET}"""
@typewriter(delay = 0.01)
def print_anim(s: str):
    import save_manager
    if save_manager.animation:
        return s
    else:
        print(s)
        return None

def display_stats(player: Player):
    """Draws a persistent HUD at the top of the screen."""
    print(f"{Colors.MAGENTA}===================================================={Colors.RESET}")
    print(
        f"{Colors.MAGENTA} ADVENTURER: {player.name} | HP: {player.health}/{player.max_health} | XP: {player.xp} {Colors.RESET}")
    print(f"{Colors.MAGENTA}===================================================={Colors.RESET}")

def is_skip_intro():
    clear_screen()
    print_anim(f"{Colors.YELLOW}Skip intro? (y/n)")
    if input(f"> {Colors.RESET}").strip() != 'y':
        clear_screen()
        display_intro()
        if input().strip():
            clear_screen()
    clear_screen()