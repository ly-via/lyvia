'''
run in visual code

wsl
source venv/bin/activate
'''

'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''
# flask: dependency in python to use other language to pass data from a database to webpage
import db, re, secrets, hashlib
from flask import Flask, request, session, render_template, abort, url_for, redirect
from flask_socketio import SocketIO
from cryptography.fernet import Fernet  # for AES encryption (storing friend usernames)
from db import encryption_key
from models import Room, OnlineUser

room = Room()
online_user = OnlineUser()
# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)
# csrf = CSRFProtect(app)
# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)
SESSION_TOKEN_DICT = {}

# don't remove this!!
import socket_routes


# -----------------------------------------------------------------------------------------


# index page
@app.route("/")
def index():
    return render_template("index.jinja")


# -----------------------------------------------------------------------------------------

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():

    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password") # user input

    # create session token, store in session cookie
    session_id = secrets.token_hex()
    SESSION_TOKEN_DICT[username] = session_id
    # assign the values
    '''
    USYD CODE CITATION ACKNOWLEDGEMENT
    I declare that the following lines of code have been taken from the
    website titled: "Flask – Sessions"
    Original URL
    https://www.tutorialspoint.com/flask/flask_sessions.htm
    Last access April, 2024
    '''
    session[f'user_{username}'] = username
    session[f'sessionID_{username}'] = session_id

    # set user who logged in as "Online"
    online_user.set_online(username)
    
    # check empty input
    if not username or not password:
        return "Error: Username and password cannot be empty!"

    # PASSWORD VERIFICATION
    '''
    USYD CODE CITATION ACKNOWLEDGEMENT
    I declare that the following lines of code have been taken from the
    website titled: "Python hashlib Module | Guide To Hashing"
    Original URL
    https://ioflood.com/blog/python-hashlib/
    Last access April, 2024
    '''
    user = db.get_user(username)
    if user is not None:
        stored_salt = db.get_salt(username)
        salt_pw = (password + stored_salt).encode()   # concatenate pw & salt from db
        hash_pw = hashlib.sha256(salt_pw).hexdigest() # hashing

    if user is None or stored_salt is None:  # username not in db
        return "Error: User does not exist!"

    if user.password != hash_pw:  # verify pw in db & user input
        return "Error: Password does not match!"
    return url_for('table', username=username)
    # return url_for('home', username=request.json.get("username"))
    # return url_for('homepage', username=username)


# -----------------------------------------------------------------------------------------


# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# check max 3 subsequent password
'''
USYD CODE CITATION ACKNOWLEDGEMENT
I declare that the following lines of code have been taken from the
website titled: "Checking for Repeating Characters in a Password Using Python - Simple Validation"
Original URL
https://www.youtube.com/watch?v=fr3SmErTlnI
Last access March, 2024
'''
@app.route("/signup")
def check_subsequent_char(password):
    last_char = None
    counter = 0
    for i in range(1, len(password)):
        last_char = password[i-1]
        if password[i] == last_char:
            counter += 1
            if counter >= 3:
                return False
        else:
            counter = 0
    return True

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password") # user input
    
    # create session token, store in session cookie
    session_id = secrets.token_hex()
    SESSION_TOKEN_DICT[username] = session_id
    # assign the values
    '''
    USYD CODE CITATION ACKNOWLEDGEMENT
    I declare that the following lines of code have been taken from the
    website titled: "Flask – Sessions"
    Original URL
    https://www.tutorialspoint.com/flask/flask_sessions.htm
    Last access April, 2024
    '''
    session[f'user_{username}'] = username
    session[f'sessionID_{username}'] = session_id

    # VALIDATE USER INPUTS
    if not username or not password:     # check empty input
        return "Error: Username and password cannot be empty!"
    
    if username.lower() == password.lower():  # check same input
        return "Error: Username and password cannot be the same!"

    # VALIDATE USERNAME
    if not len(username) >= 5 or not username.isalnum():
        return """Error: Username should be:
- At least 5 characters long
- Only contain letters and numbers
- Contain no special characters, spaces and symbols"""

    # VALIDATE STRONG PASSWORD
    # re.search -- at most 3 repeating characters
    '''
    USYD CODE CITATION ACKNOWLEDGEMENT
    I declare that the following lines of code have been taken from the
    website titled: 
    - "Checking the strength of a password (how to check conditions)"
    - 'Determine if string has 3 or more duplicate sequential characters in Python"
    Original URL
    - https://stackoverflow.com/questions/16709638/checking-the-strength-of-a-password-how-to-check-conditions
    - https://stackoverflow.com/questions/28007101/determine-if-string-has-3-or-more-duplicate-sequential-characters-in-python
    Last access March, 2024
    '''
    not_subsequent = check_subsequent_char(password)
    
    if not 8 < len(password) < 20 or \
        password.lower() == password or \
        password.upper() == password or \
        password.isalnum() or \
        re.search(r'(.)\1\1', password) or \
        not not_subsequent or \
        not any(i.isdigit() for i in password):
        return """Error: Password should be:
- Length between 8 and 20 characters
- Contain lowercase and uppercase letters
- Contain numbers\n- Contain symbols
- At most 3 repeating and subsequent characters"""
    
    user = db.get_user(username)
    if user is None:  # username not in db : NEW USER
        # salting
        salt = secrets.token_hex(16)
        salt_pw = password + salt

        # hashing
        '''
        USYD CODE CITATION ACKNOWLEDGEMENT
        I declare that the following lines of code have been taken from the
        website titled: "Adding Salt to Hashing: A Better Way to Store Passwords"
        Original URL
        https://auth0.com/blog/adding-salt-to-hashing-a-better-way-to-store-passwords/
        Last access April, 2024
        '''
        password = hashlib.sha256(salt_pw.encode()).hexdigest()
        db.insert_user(username, password, salt)    # insert data into db
        return url_for('table', username=username)  # direct to homepage
    else:
        if user.username == username: # user alr registered
            return "Error: User already exists!"


# -----------------------------------------------------------------------------------------


######     WITH CHECKBOXES IN FRIEDNLIST     ######
# handles a get request to display friend list
@app.route("/friendlist", methods=["GET", "POST"])  # have to have both GET, POST
def display_friendlist():

    username = request.args.get("username")
    online_friend = request.form.get("online_friend")  # from jinja form method="POST"
    
    # create new session for mapping user and selected online friend
    # to be checked in homepage since "online_friend" is part of the url
    session[f'onlineFriend_{username}'] = online_friend

    # -- SESSION TOKEN VERIFICATION -- used in every function!
    # REF : 1) https://www.tutorialspoint.com/flask/flask_sessions.htm
    '''
    USYD CODE CITATION ACKNOWLEDGEMENT
    I declare that the following lines of code have been taken from the
    website titled: "How to use Flask-Session in Python Flask ?"
    Original URL
    https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
    Last access April, 2024
    '''
    # check username
    if not f'user_{username}' in session:
        return redirect(url_for('login'))
    
    # check session ID key
    sessionID_key = f'sessionID_{username}'
    if not sessionID_key in session:
        return redirect(url_for('login'))
    
    # check session token
    if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
        return redirect(url_for('login'))
    # -- END OF SESSION VERIFICATION --
    
    friend_usernames = db.get_approved_request(username)
    # for cases when the friend request is one-way request
    if not friend_usernames:
        # SESSION TOKEN VERIFICATION
        if not f'user_{username}' in session:
            return redirect(url_for('login'))
        sessionID_key = f'sessionID_{username}'
        if not sessionID_key in session:
            return redirect(url_for('login'))
        if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
            return redirect(url_for('login'))
        another_friend_usernames = db.another_approved_request(username)
    another_friend_usernames = db.another_approved_request(username)

    # create dictionary to store {username: online_status}
    friend_status = {}
    for friends in friend_usernames:
        friend_status[friends] = online_user.is_online(friends)
    for friends in another_friend_usernames:
        friend_status[friends] = online_user.is_online(friends)
    
    # check jinja template if "Chat" button is clicked 
    action = request.form.get("action")
    if action == "chat":
        # SESSION TOKEN VERIFICATION
        if not f'user_{username}' in session:
            return redirect(url_for('login'))
        sessionID_key = f'sessionID_{username}'
        if not sessionID_key in session:
            return redirect(url_for('login'))
        if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
            return redirect(url_for('login'))
        # redirect to homepage ONLY after "Chat" button is clicked
        return redirect(url_for('homepage', username=username, online_friend=online_friend))
    return render_template("friendlist.jinja", username=username, friend_usernames=friend_usernames, another_friend_usernames=another_friend_usernames, friend_status=friend_status, online_friend=online_friend)


# -----------------------------------------------------------------------------------------


# handles a get request to add friend
@app.route("/addfriend", methods=["GET", "POST"])
def add_friend():

    username = request.args.get("username")

    # -- SESSION TOKEN VERIFICATION --
    if not f'user_{username}' in session:
        return redirect(url_for('login'))

    sessionID_key = f'sessionID_{username}'
    if not sessionID_key in session:
        return redirect(url_for('login'))
    if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
        return redirect(url_for('login'))
    
    # user input for add friend textbox
    friend = request.form.get("receiver")
    # get all the added friends for the user who logged in
    friend_usernames = db.for_add_friend(username)  

    if request.method == "GET":
        # -- SESSION TOKEN VERIFICATION --
        if not f'user_{username}' in session:
            return redirect(url_for('login'))

        sessionID_key = f'sessionID_{username}'
        if not sessionID_key in session:
            return redirect(url_for('login'))
        if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
            return redirect(url_for('login'))
        return render_template("addfriend.jinja", username=username, friend_usernames=friend_usernames)
    
    elif request.method == "POST":
        # -- SESSION TOKEN VERIFICATION --
        if not f'user_{username}' in session:
            return redirect(url_for('login'))

        sessionID_key = f'sessionID_{username}'
        if not sessionID_key in session:
            return redirect(url_for('login'))
        if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
            return redirect(url_for('login'))

        friend_username = db.get_user(friend)  # get username from db
        # no such username in db
        if friend_username is None:  
            error_message = "Unknown username!"
        # user adding him/herself
        elif username == friend:  
            error_message = "You can't add yourself as friend!"
        # already added as friend
        elif friend in friend_usernames: 
            error_message = f"Friend request is already sent to '{friend}'."
        else:
            # ENCRYPTION to store friend's username securely
            # use the consistent encryption key from db
            '''
            USYD CODE CITATION ACKNOWLEDGEMENT
            I declare that the following lines of code have been taken from the
            website titled: "Fernet (symmetric encryption) using Cryptography module in Python"
            Original URL
            https://www.geeksforgeeks.org/fernet-symmetric-encryption-using-cryptography-module-in-python/
            Last access April, 2024
            '''
            key_value = Fernet(encryption_key)
            # encode() -> convert from string to bytes datatype & encrypt
            encrypted_username = key_value.encrypt(friend.encode())
            # store encrypted friend's username into db
            # encrypt on client-side before sending to the server/database)
            db.insert_friend(username, encrypted_username)
            msg = f"Friend request sent to '{friend}' successfully!"
            return render_template("addfriend.jinja", username=username, friend_usernames=friend_usernames, msg=msg)
    return render_template("addfriend.jinja", username=username, friend_usernames=friend_usernames, error_message=error_message)


# ------------------------------------------------------------------------------------------


# handles a get request to display friend requests
@app.route("/friendrequest")
def display_friendrequest():
    username = request.args.get("username")

    # -- SESSION TOKEN VERIFICATION --
    if not f'user_{username}' in session:
        return redirect(url_for('login'))

    sessionID_key = f'sessionID_{username}'
    if not sessionID_key in session:
        return redirect(url_for('login'))
    if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
        return redirect(url_for('login'))

    senders = db.get_sent_requests(username)      # for "SENT"
    friends = db.get_received_requests(username)  # for "RECEIVED"
    return render_template("friendrequest.jinja", username=username, senders=senders, friends=friends)


# -----------------------------------------------------------------------------------------


@app.route("/update_friend_request", methods=["POST"])
def update_friend_request():
    username = request.form.get("username")  # request.form.get() -> form method="POST"
    senders = db.get_sent_requests(username)      # for "SENT"
    friends = db.get_received_requests(username)  # for "RECEIVED"
    message = None
    error_message = None
    
    action = request.form.get("action")  # get buttons action from jinja file
    if action == "approve" or action == "reject":  # check valid button action
        friend_usernames = request.form.getlist("friends")
        
        # pass into db to handle different action
        for friend_username in friend_usernames:
            db.update_request_status(username, friend_username, action)
        if action == "approve":
            message = "Friend requests approved successfully!"
        else:
            message = "Friend requests rejected successfully!"
    else:
        error_message = "Error: Invalid button action."
    return render_template("friendrequest.jinja", username=username, senders=senders, friends=friends, message=message, error_message=error_message)


# -----------------------------------------------------------------------------------------


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404


# -----------------------------------------------------------------------------------------


# home page, where the messaging app is
@app.route("/home", methods=['GET'])
def homepage():
    if request.args.get("username") is None:
        abort(404)
    
    # request.args.get -- getting from the url
    username = request.args.get("username")
    online_f = request.args.get("online_friend")

    # SESSION TOKEN VERIFICATION
    # check username
    if not f'user_{username}' in session:
        return redirect(url_for('login'))
    
    # check session ID key
    sessionID_key = f'sessionID_{username}'
    if not sessionID_key in session:
        return redirect(url_for('login'))
    
    # check session token
    if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
        return redirect(url_for('login'))
    
    # check if the right selected online friend is in the session
    # mapping to "onlineFriend_{username} : {online_f}"
    session_online_friend = session.get(f'onlineFriend_{username}')
    if session_online_friend != online_f:
        # print(session)
        return redirect(url_for('login'))

    # this affecting homepage url -- online friend parsed
    return render_template("home.jinja", username=username,online_friend=online_f)


# -----------------------------------------------------------------------------------------


@app.route("/table")
def table():
    if request.args.get("username") is None:
        abort(404)
    username = request.args.get("username")

    # -- SESSION TOKEN VERIFICATION --
    # verify each distinct username in each session token
    if not f'user_{username}' in session:
        return redirect(url_for('login'))
    
    # get each distinct session id mapping to each username
    sessionID_key = f'sessionID_{username}'
    if not sessionID_key in session:
        return redirect(url_for('login'))
    
    # if username & session_id is not mapped in session token dict
    if SESSION_TOKEN_DICT.get(username) != session[sessionID_key]:
        return redirect(url_for('login'))
    return render_template("table.jinja", username=request.args.get("username"))


# -----------------------------------------------------------------------------------------


# for Jinja files debug
@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))
        # return ''
    return dict(mdebug=print_in_console)


# -----------------------------------------------------------------------------------------


if __name__ == '__main__':
    # socketio.run(app)
    app.run(ssl_context=('./CERTIFICATES/localhost.crt',
                         './CERTIFICATES/localhost.key'))