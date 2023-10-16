
from pynput import mouse,keyboard
from time import sleep
from PIL import ImageGrab
import ctypes
PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
Mouse = mouse.Controller()
Key = keyboard.Controller()
print(Mouse.position)
sleep(2)
img = ImageGrab.grab()
print(img.size)
print(Mouse.position)