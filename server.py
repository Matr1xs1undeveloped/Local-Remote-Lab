#DO NOT CHANGE! this contains core parts for the server to boot and work 
from flask import Flask, render_template, request
from auth import requires_auth
import actions
import screen
import os
import subprocess

app = Flask(__name__)

screen.start_screenshot_thread(fps=5, quality=50)

#blacklisted for security measures, if you know what youre doing
#you can remove some things from the list
BLACKLIST = [
    "format", "shutdown", "del C:\\", "rd /s /q", "diskpart", 
    "bcdedit", "cipher", "taskkill /f /pid 0", "reg delete", "bootrec"
]
#calls the index.html
@app.route("/")
@requires_auth
def index():
    cpu, ram = actions.get_system_usage()
    desktop_files = actions.list_desktop()
    return render_template("index.html", cpu=cpu, ram=ram, desktop_files=desktop_files)

@app.route("/create_folder", methods=["POST"])
@requires_auth
def create_folder():
    folder_name = request.form.get("folder_name")
    if folder_name:
        msg = actions.create_folder(folder_name)
        return f"<p>{msg}</p><a href='/'>Back</a>"
    return "<p>No folder name provided</p><a href='/'>Back</a>"

@app.route("/shutdown", methods=["POST"])
@requires_auth
def shutdown():
    msg = actions.shutdown_pc(delay=5)
    return f"<p>{msg}</p><a href='/'>Back</a>"

@app.route("/delete_file", methods=["POST"])
@requires_auth
def delete_file():
    file_name = request.form.get("file_name")
    if file_name:
        msg = actions.delete_file(file_name)
        return f"<p>{msg}</p><a href='/'>Back</a>"
    return "<p>No file/folder name provided</p><a href='/'>Back</a>"

@app.route("/overlay", methods=["POST"])
@requires_auth
def overlay():
    text = request.form.get("overlay_text", "Hello")
    msg = actions.show_overlay(text)
    return f"<p>{msg}</p><a href='/'>Back</a>"

@app.route("/list_processes", methods=["GET"])
@requires_auth
def list_processes():
    processes = actions.list_processes()
    return "<p>" + "<br>".join(processes) + "</p><a href='/'>Back</a>"

@app.route("/advanced_startup", methods=["POST"])
@requires_auth
def advanced_startup():
    return f"<p>{actions.advanced_startup()}</p><a href='/'>Back</a>"

@app.route("/rename_desktop", methods=["POST"])
@requires_auth
def rename_desktop():
    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")
    if old_name and new_name:
        msg = actions.rename_desktop(old_name, new_name)
        return f"<p>{msg}</p><a href='/'>Back</a>"
    return "<p>Missing names</p><a href='/'>Back</a>"

@app.route("/create_text_file", methods=["POST"])
@requires_auth
def create_text_file():
    filename = request.form.get("filename")
    content = request.form.get("content", "")
    if filename:
        msg = actions.create_text_file(filename, content)
        return f"<p>{msg}</p><a href='/'>Back</a>"
    return "<p>No filename provided</p><a href='/'>Back</a>"

@app.route("/batch_editor")
@requires_auth
def batch_editor():
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
    
    folder_path = os.path.join("batch_files", filename)
    
    with open(folder_path, "w") as f:
        f.write(content)
    
    try:
        subprocess.Popen(folder_path, shell=True)
    except Exception as e:
        return f"<p>Error executing batch: {e}</p><a href='/batch_editor'>Back</a>"
    
    return "<p>Batch executed successfully!</p><a href='/'>Back to Lab</a>"

if __name__ == "__main__":
    from waitress import serve
    print("Server starting on all interfaces, port 5000...") #you can change the port number on the message if u changed it
    serve(app, host="0.0.0.0", port=5000) #if port 5000 isnt available for you, feel free to remove it and try out other ports