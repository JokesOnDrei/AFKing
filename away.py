import pyautogui
import time
import random
import threading
from pynput import keyboard

esc_press_count = 0
stop_event = threading.Event()

# Set screen size boundaries
screen_width, screen_height = pyautogui.size()

def on_press(key):
    global esc_press_count
    try:
        if key == keyboard.Key.esc:
            esc_press_count += 1
            print(f"Esc pressed {esc_press_count} time(s)")
            if esc_press_count >= 3:
                stop_event.set()
        else:
            esc_press_count = 0  # reset count if any other key is pressed
    except:
        pass

def move_mouse_randomly():
    while not stop_event.is_set():
        x = random.randint(10, screen_width - 10)
        y = random.randint(10, screen_height - 10)
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(5)  # delay 5 seconds between each move

if __name__ == '__main__':
    # Start listening to the keyboard
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print("Mouse will now move randomly. Press 'Esc' 3 times to stop.")
    move_mouse_randomly()
    print("Script stopped.")