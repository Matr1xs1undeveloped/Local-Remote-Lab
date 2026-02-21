#dont change any modules or else this part will not work
from functools import wraps
from flask import request, Response
#password only prompt, you can change this if you want to
PASSWORD = "Adminlol"

#password only check, username is free to use
def check_auth(username, password):
    """Accept any username, check only password"""
    return password == PASSWORD

#authentication if password is correct
def authenticate():
    """Prompt login"""
    return Response(
        'Could not verify your access.\n'
        'Please provide a username and password.', 401,
        {'WWW-Authenticate': 'Basic realm="Cyberpunk Lab"'})

#self explanatory
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        print(f"[LOGIN] User '{auth.username}' accessed the Lab.")
        return f(*args, **kwargs)
    return decorated