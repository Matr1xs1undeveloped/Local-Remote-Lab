#changing these imports or deleting them will break core parts of the system, so dont do that unless you know what youre doing
from flask import Flask, render_template, request, jsonify
from auth import requires_auth
import actions
import screen
import os
import subprocess
import logging
import threading
import time
from datetime import datetime
import sys

app = Flask(__name__)

# desktop path (you can change this if you have it saved on another path but i recommend putting the complete Lab file on the desktop)
def get_desktop():
    return os.path.join(os.path.expanduser("~"), "Desktop")

# Autostart setup (breaks if theres no connection of internet on startup)
def setup_autostart():
    try:
        startup_folder = os.path.join(
            os.environ["APPDATA"],
            r"Microsoft\Windows\Start Menu\Programs\Startup"
        )
        vbs_path = os.path.join(startup_folder, "lab_server_start.vbs")
        if os.path.exists(vbs_path):
            return
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        server_path = os.path.abspath(__file__)
        script = f'''
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "{pythonw} {server_path}", 0, False
'''
        with open(vbs_path, "w") as f:
            f.write(script)
        print("Startup entry created.")
    except Exception as e:
        print("Startup setup failed:", e)

# Log file setup (you cant delete the snippet or make it into a comment using # if you dont want it on  the dashboard)
logger = logging.getLogger("lab")
logger.setLevel(logging.INFO)

def log_worker():
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_path = os.path.join(get_desktop(), f"lab_log_{timestamp}.txt")
            logger.handlers.clear()
            handler = logging.FileHandler(log_path, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
            logger.addHandler(handler)
            logger.info("server running")
        except Exception as e:
            print("Logging error:", e)
        time.sleep(300)

threading.Thread(target=log_worker, daemon=True).start()

# Screenshot thread
def safe_start_screenshot_thread():
    def worker():
        while True:
            try:
                logger.info("starting screenshot thread")
                screen.start_screenshot_thread(fps=5, quality=50)
                return
            except Exception as e:
                print("Screenshot failed — retrying in 10s:", e)
                logger.info(f"screenshot failed: {e}")
                time.sleep(10)
    threading.Thread(target=worker, daemon=True).start()
safe_start_screenshot_thread()

BLACKLIST = ["shutdown"]

# rest of the routes
@app.route("/")
@requires_auth
def index():
    logger.info("homepage visited")
    cpu, ram = actions.get_system_usage()
    desktop_files = actions.list_desktop()
    return render_template("index.html", cpu=cpu, ram=ram, desktop_files=desktop_files)

@app.route("/create_folder", methods=["POST"])
@requires_auth
def create_folder():
    folder_name = request.form.get("folder_name")
    if folder_name:
        logger.info(f"create_folder {folder_name}")
        msg = actions.create_folder(folder_name)
        return f"<p>{msg}</p><a href='/'>Back</a>"
    return "<p>No folder name provided</p><a href='/'>Back</a>"

@app.route("/shutdown", methods=["POST"])
@requires_auth
def shutdown():
    logger.info("shutdown requested")
    msg = actions.shutdown_pc(delay=5)
    return f"<p>{msg}</p><a href='/'>Back</a>"

@app.route("/delete_file", methods=["POST"])
@requires_auth
def delete_file():
    file_name = request.form.get("file_name")
    if file_name:
        logger.info(f"delete_file {file_name}")
        msg = actions.delete_file(file_name)
        return f"<p>{msg}</p><a href='/'>Back</a>"
    return "<p>No file/folder name provided</p><a href='/'>Back</a>"

@app.route("/overlay", methods=["POST"])
@requires_auth
def overlay():
    text = request.form.get("overlay_text", "Hello")
    logger.info(f"overlay {text}")
    msg = actions.show_overlay(text)
    return f"<p>{msg}</p><a href='/'>Back</a>"

@app.route("/list_processes", methods=["GET"])
@requires_auth
def list_processes():
    logger.info("list_processes")
    processes = actions.list_processes()
    return "<p>" + "<br>".join(processes) + "</p><a href='/'>Back</a>"

@app.route("/advanced_startup", methods=["POST"])
@requires_auth
def advanced_startup():
    logger.info("advanced_startup")
    return f"<p>{actions.advanced_startup()}</p><a href='/'>Back</a>"

@app.route("/rename_desktop", methods=["POST"])
@requires_auth
def rename_desktop():
    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")
    if old_name and new_name:
        logger.info(f"rename {old_name} -> {new_name}")
        msg = actions.rename_desktop(old_name, new_name)
        return f"<p>{msg}</p><a href='/'>Back</a>"
    return "<p>Missing names</p><a href='/'>Back</a>"

@app.route("/create_text_file", methods=["POST"])
@requires_auth
def create_text_file():
    filename = request.form.get("filename")
    content = request.form.get("content", "")
    if filename:
        logger.info(f"create_text_file {filename}")
        msg = actions.create_text_file(filename, content)
        return f"<p>{msg}</p><a href='/'>Back</a>"
    return "<p>No filename provided</p><a href='/'>Back</a>"

@app.route("/batch_editor")
@requires_auth
def batch_editor():
    logger.info("batch_editor opened")
    return render_template("batch_editor.html")

@app.route("/save_batch", methods=["POST"])
@requires_auth
def save_batch():
    filename = request.form.get("filename")
    content = request.form.get("content", "")
    if not filename:
        return "<p>No filename provided</p><a href='/batch_editor'>Back</a>"
    for bad in BLACKLIST:
        if bad.lower() in content.lower():
            return f"<p>Blocked dangerous command: {bad}</p><a href='/batch_editor'>Back</a>"
    if not filename.endswith(".bat"):
        filename += ".bat"
    os.makedirs("batch_files", exist_ok=True)
    file_path = os.path.join("batch_files", filename)
    with open(file_path, "w") as f:
        f.write(content)
    try:
        logger.info(f"execute_batch {filename}")
        subprocess.Popen(file_path, shell=True)
    except Exception as e:
        return f"<p>Error executing batch: {e}</p><a href='/batch_editor'>Back</a>"
    return "<p>Batch executed successfully!</p><a href='/'>Back to Lab</a>"

#keyboard and mouse accessibillity (not finished yet)
@app.route("/send_key", methods=["POST"])
@requires_auth
def send_key():
    data = request.get_json()
    key = data.get("key")
    if key:
        actions.press_key(key)
    return jsonify({"status": "ok"})

@app.route("/mouse_move", methods=["POST"])
@requires_auth
def mouse_move():
    data = request.get_json()
    x, y = data.get("x"), data.get("y")
    actions.move_mouse(x, y)
    return jsonify({"status": "ok"})

@app.route("/mouse_click", methods=["POST"])
@requires_auth
def mouse_click():
    data = request.get_json()
    button = data.get("button", 0)
    actions.click_mouse(button)
    return jsonify({"status": "ok"})
#core part, do not change unless fatal error or experienced
if __name__ == "__main__":
    setup_autostart()
    from waitress import serve
    logger.info("server started")
    print("Server starting on all interfaces, port 5000...")
    serve(app, host="0.0.0.0", port=5000) #dont change 0.0.0.0 unless you only want it to run locally without access with another device
    #if port 5000 is blocked on your network you can change it but make sure to update the port in the url when you access it
