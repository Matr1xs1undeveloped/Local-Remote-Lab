import threading
import time
from PIL import ImageGrab

latest_screenshot = "static/screen.png" #this is a hardcoded path do not change unless you
#moved the screen.png somewhere else

#do not change any of the values or the website could expect crashes or slowdowns
def capture_screen_loop(fps=5, quality=50):
    """Capture screen continuously and save as JPEG"""
    interval = 1 / fps
    while True:
        screenshot = ImageGrab.grab().resize((640, 360))
        screenshot.save(latest_screenshot, quality=quality)
        time.sleep(interval)

def start_screenshot_thread(fps=5, quality=50):
    thread = threading.Thread(target=capture_screen_loop, args=(fps, quality), daemon=True)
    thread.start()