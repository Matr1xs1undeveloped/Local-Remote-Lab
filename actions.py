#changing these can break core parts of the program
import os
import psutil
import time
from pathlib import Path
import subprocess
import tkinter as tk
import pyautogui

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")#desktop path, which is why i recommend to keep the whole folder on the desktop

def show_overlay(text, duration=3):
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    label = tk.Label(root, text=text, font=("Consolas", 24), bg="black", fg="#b19cd9")
    label.pack()
    root.update_idletasks()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry(f"+{w//2 - label.winfo_reqwidth()//2}+{h//2 - label.winfo_reqheight()//2}")
    root.after(duration*1000, root.destroy)
    root.mainloop()
    return f"Overlay shown: {text}"

#all the functions (if youre experienced then you can add your own lol)
def list_processes():
    return [p.name() for p in psutil.process_iter()]

def get_system_usage():
    return psutil.cpu_percent(interval=1), psutil.virtual_memory().percent

def list_desktop():
    return [f.name for f in Path(DESKTOP).iterdir()]

def rename_desktop(old_name, new_name):
    old_path = os.path.join(DESKTOP, old_name)
    new_path = os.path.join(DESKTOP, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        return f"Renamed {old_name} → {new_name}"
    return f"{old_name} not found"

def create_text_file(filename, content=""):
    path = os.path.join(DESKTOP, filename)
    if not filename.endswith(".txt"):
        path += ".txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Created text file: {os.path.basename(path)}"

def advanced_startup():
    try:
        subprocess.run("shutdown /r /o /f /t 0", shell=True)
        return "PC restarting to advanced startup..."
    except Exception as e:
        return f"Failed to start advanced startup: {e}"

def create_folder(folder_name):
    path = os.path.join(DESKTOP, folder_name)
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {folder_name}"
    except Exception as e:
        return f"Failed to create folder: {e}"

def delete_file(file_name):
    path = os.path.join(DESKTOP, file_name)
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"File deleted: {file_name}"
        elif os.path.isdir(path):
            os.rmdir(path)
            return f"Folder deleted: {file_name}"
        return f"{file_name} not found"
    except Exception as e:
        return f"Failed to delete: {e}"

def shutdown_pc(delay=5):
    try:
        time.sleep(delay)
        subprocess.Popen("shutdown /s /t 0", shell=True)
        return f"PC will shutdown in {delay} seconds."
    except Exception as e:
        return f"Failed to shutdown: {e}"

def log_test():
    print("Log test button pressed!")
    return "Log test executed."

# --- Keyboard & Mouse ---
def press_key(key):
    try:
        pyautogui.press(key.lower())
    except Exception:
        print(f"Failed to press key: {key}")

def move_mouse(x, y):
    screen_width, screen_height = pyautogui.size()
    px = int(x / 480 * screen_width)
    py = int(y / 270 * screen_height)
    pyautogui.moveTo(px, py)

def click_mouse(button):
    btn = 'left' if button == 0 else 'right'
    pyautogui.click(button=btn)
