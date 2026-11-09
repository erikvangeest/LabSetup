from threading import Thread
import pyautogui
import time

time.sleep(10)
while True:
    pyautogui.click()         # Clicks at current mouse position
    time.sleep(6 * 60 * 60)   # Waits 6 hours (6 hours * 60 minutes * 60 seconds)