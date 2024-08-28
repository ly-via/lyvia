'''
socket_routes
file containing all the routes related to socket.io
'''

import db, hashlib, hmac
from flask_socketio import join_room, emit, leave_room
from flask import request
from models import Room
from models import Article
# from Crypto.PublicKey import RSA
# from Crypto.Cipher import PKCS1_OAEP

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

room = Room()
article = Article()

# -----------------------------------------------------------------------------------------

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))
    

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))


# -----------------------------------------------------------------------------------------


############ OAEP -- EN/DECRYPTING MSG all in py file ############

public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD3R2ufISIIgYH2wIZroL8gtgZb
Gtn1fyR0kU2RJ1LCMX38waRVL5nuHSYqXCl4QKktjSy9gzTavoh2rTZ0n7U0zHCn
7qgs67uCY69aAkqe57JlTEERXIvnrPQf8/Ia/oh6J+upnfMlXe/qqXFetzyK/dA0
jJI492M3ahmT7J3pAQIDAQAB
-----END PUBLIC KEY-----"""

filename = "CERTIFICATES/msgEncrypt.pem"
def get_private_key(filename):
    with open(filename, "rb") as file:
        private_key = file.read()
    return private_key

'''
USYD CODE CITATION ACKNOWLEDGEMENT
I declare that the following lines of code have been taken from the
website titled: 
- "PKCS#1 OAEP (RSA)"
- "NotImplementedError: Use module Crypto.Cipher.PKCS1_OAEP instead error"
Original URL
- https://pycryptodome.readthedocs.io/en/latest/src/cipher/oaep.html
- https://stackoverflow.com/questions/44427934/notimplementederror-use-module-crypto-cipher-pkcs1-oaep-instead-error
Last access April, 2024

def decrypt_msg(encrypted_msg, private_key):
    private_key_obj = RSA.importKey(private_key)
    cipher = PKCS1_OAEP.new(private_key_obj)
    decrypted_msg = cipher.decrypt(encrypted_msg)
    return decrypted_msg.decode()

def encrypt_msg(message, public_key):
    receiver_key = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(receiver_key)
    encrypted_msg = cipher.encrypt(message.encode())
    return encrypted_msg
'''
# -----------------------------------------------------------------------------------------

def get_mac(username, receiver, room_id):
    # use user's password as the secret key
    user_pw = db.get_password(username)
    if not user_pw:
        return "Error with secret key: User not found!"
    encrypted_msg = db.get_encrypted_msg(username, receiver)  # in list type
    for msg in encrypted_msg:  # convert into string
        msg_in_str = ''.join([str(msg)])

    '''
    USYD CODE CITATION ACKNOWLEDGEMENT
    I declare that the following lines of code have been taken from the
    website titled: "Python encoded message with HMAC-SHA256"
    Original URL
    https://stackoverflow.com/questions/38133665/python-encoded-message-with-hmac-sha256
    Last access April, 2024
    '''
    user_pw_in_bytes = user_pw.encode('utf-8')  # convert string into bytes
    mac = hmac.new(user_pw_in_bytes, msg_in_str.encode(), hashlib.sha256).hexdigest()
    return mac

'''
USYD CODE CITATION ACKNOWLEDGEMENT
I declare that the following lines of code have been taken from the
website titled: "Digital Signature Verification with Python and hmac"
Original URL
https://gist.github.com/craigderington/9cb3ffaf4279af95bebcc0470212f788
Last access April, 2024
'''
def verify_mac(msg, received_mac, username):
    user_pw = db.get_password(username)
    user_pw_in_bytes = user_pw.encode('utf-8')
    mac = hmac.new(user_pw_in_bytes, msg.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(received_mac, mac)

# -----------------------------------------------------------------------------------------

@socketio.on("enter_chatroom")
def display_msg_history(room_id, username, receiver):

    # print(f'checkkkkkkkk -- {username} -- {receiver}')

    if username and receiver:
        msg_history_ls = db.get_encrypted_msg(username, receiver)
        # get sender, encrypted msg from db for that room_id looping history_ls
        for sender, msg_history in msg_history_ls:
            # private_key = get_private_key(filename)
            # decrypted_msg_str = decrypt_msg(msg_history, private_key)
            # only emit and print the ones with actual msg history
            # to avoid printing empty message histories
            # it's a bad way to do it though :(
            if len(msg_history_ls) > 0:
                role = db.get_role(sender)
                emit("incoming", (f"{sender} ({role}): {msg_history}", "#a6a6a6"))

# -----------------------------------------------------------------------------------------

@socketio.on("send")
def send(username, receiver, message, room_id):

    # encrypt plaintext msg
    # encrypted_msg = encrypt_msg(message, public_key)
    # insert into db with those data
    if len(message) > 0:
        db.insert_encrypted_msg(room_id, username, receiver, message)
        # private_key = get_private_key(filename)     # decrypt
        # decrypted_msg = decrypt_msg(encrypted_msg, private_key)

    # HMAC - to authenticate ALL msg
    # use ALL msg to generate & verify HMAC
    if username and receiver:
        db_encrypted_msg = db.get_encrypted_msg(username, receiver)
        if db_encrypted_msg:
            for msg in db_encrypted_msg:
                msg_in_str = ''.join([str(msg)])

            # mac = get_mac(username, receiver, room_id)
            # is_valid_mac = verify_mac(msg_in_str, mac, username)
            # is_valid_mac = verify_mac(decrypted_msg, mac, username)
            # if not is_valid_mac:
            #     print("ALERT! ALERT! ALERT! MAC verification failed!!!")
            #     return "ALERT! ALERT! ALERT! MAC verification failed!!!"
            emit("incoming", (f"{username}: {message}"), to=room_id)

################# EN/DECRYPTING MSG all in py file ^ ##################


# -----------------------------------------------------------------------------------------

# sent when the user joins a room
# join room event handler
@socketio.on("join")
def join(sender_name, receiver_name):
    # print(f"joinnnnnnnnnn --- {sender_name}, {receiver_name}")

    receiver = db.get_user(receiver_name)
    # if receiver is None:
    #     return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)
    # if the user is already inside of a room 
    if room_id is not None and receiver is not None:  
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        
        # only emit when there is value for receiver
        if receiver_name or receiver_name != '':
            # emit only to the sender
            emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        return room_id

    # if the user isn't inside of any room, create a new room 
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    
    # only emit when there is value for receiver
    if receiver_name or receiver_name != '':
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id


# -----------------------------------------------------------------------------------------


# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)


# -----------------------------------------------------------------------------------------


@socketio.on("notification")
def for_notification(username, receiver, visited):

    unread_msg, group_chat_counter, single_chat_counter, group_friend = db.get_notification(username)
   
    # print(f'in pyyyyyyyyy -- {unread_msg}, {group_chat_counter}, {single_chat_counter}, {group_friend}')

    if unread_msg is not None:
        single_sender_ls = []
        group_sender_ls = []

        for sender, msg_type, receivers in unread_msg:
            if msg_type == 'single':
                single_sender_ls.append(sender)
            elif msg_type == 'group':
                group_sender_ls.append(sender)

        if single_chat_counter > 0:
            for sender in single_sender_ls:
                emit("notification", (f"You have new message from '{sender}'.", "True"))
        if group_chat_counter > 0:
            for sender in group_sender_ls:
                emit("notification", (f"You have new message from '{sender}' in group chat with '{group_friend}'.", "True"))
    
    if not unread_msg:
        emit("notification", ("You have no new message."))


@socketio.on("update_notification")
def update_is_read(username, receiver):
    # print(f"socketioooooooooooooo -- {username} , {receiver}")
    db.update_is_read(username, receiver)


# -----------------------------------------------------------------------------------------


@socketio.on("view_article")
def view_article():
    articles = db.get_article()
    if articles:
        emit("view_article_response", articles)
    else:
        emit("view_article_response", "Article not found!")


@socketio.on("create_new_article")
def create_new_article(username, user_id, role, title, content, post_private):
    db.insert_new_article(username, user_id, role, title, content, post_private)

    # to show the new created article immediately
    updated_articles = db.get_article()
    emit("view_article_response", updated_articles)


# -----------------------------------------------------------------------------------------


@socketio.on("insert_new_comment")
def insert_new_comment(article_id, username, user_id, role, comment):
    # commit to db
    db.insert_new_comment(article_id, username, user_id, role, comment)
    
    # to show the new created article immediately
    updated_comments = db.show_comment(article_id)
    emit("display_comment", updated_comments)


@socketio.on("show_comment")
def show_comment(article_id):
    comments = db.show_comment(article_id)
    if comments:
        emit("display_comment", comments)
    else:
        emit("display_comment", "No comment...")


# -----------------------------------------------------------------------------------------


@socketio.on("edit_article")
def edit_article(article_id, title, content):
    # update and commit to db
    db.edit_article(article_id, title, content)
    
    updated_articles = db.get_article()
    emit("view_article_response", updated_articles)
    
    # get the updated article to show on content immediately
    edited_article = db.get_selected_article(article_id)
    emit("view_content_response", edited_article)


# -----------------------------------------------------------------------------------------


@socketio.on("delete_article")
def delete_article(article_id):
    db.delete_article(article_id)
    
    updated_articles = db.get_article()
    emit("view_article_response", updated_articles)
    
    # get the updated article to show on content immediately
    if not updated_articles:
        edited_article = None
    else:
        edited_article = db.get_selected_article(updated_articles[0]['article_id'])
    emit("view_content_response", edited_article)


# -----------------------------------------------------------------------------------------


@socketio.on("delete_comment")
def delete_comment(article_id, content):

    the_comment_id = db.get_comment_id(article_id, content)
    db.delete_comment(the_comment_id)
    
    updated_articles = db.get_article()
    emit("view_article_response", updated_articles)
    
    # get the updated article
    if not updated_articles:
        edited_article = None
    else:
        edited_article = db.get_selected_article(updated_articles[0]['article_id'])
    emit("view_content_response", edited_article)

    # get the updated comments
    comments = db.show_comment(article_id)
    if comments:
        emit("display_comment", comments)
    else:
        emit("display_comment", "No comment...")


# -----------------------------------------------------------------------------------------


@socketio.on("mute_user")
def mute_user(muted_username):

    the_username = db.get_user(muted_username)  # check username in db

    if the_username is None:
        msg = "Unknown username!"
        emit("for_NONE_mute_user", msg)
    else:
        # the username exists in DB, proceed to mute the user
        db.mute_user(muted_username)
        is_muted_after_muted = db.get_is_muted(muted_username)

        msg = "Muted the user successfully!"
        emit("for_YES_mute_user", msg)
        # emit("user_muted", muted_username, is_muted_after_muted, broadcast=True)
        emit("user_muted", {'muted_username': muted_username, 'is_muted_after_muted': is_muted_after_muted}, broadcast=True)


# -----------------------------------------------------------------------------------------


@socketio.on("unmute_user")
def unmute_user(unmuted_username):

    the_username = db.get_user(unmuted_username)  # check username in db

    if the_username is None:
        msg = "Unknown username!"
        emit("for_NONE_mute_user", msg)
    else:
        db.unmute_user(unmuted_username)
        is_muted_after_UNmuted = db.get_is_muted(unmuted_username)
        
        msg = "Unmuted the user successfully!"
        emit("for_YES_mute_user", msg)
        # emit("user_unmuted", unmuted_username, broadcast=True)
        emit("user_unmuted", {'unmuted_username': unmuted_username, 'is_muted_after_UNmuted': is_muted_after_UNmuted}, broadcast=True)


# -----------------------------------------------------------------------------------------


@socketio.on("assign_role")
def assign_role(assigned_username, assigned_role):

    the_username = db.get_user(assigned_username)  # check username in db

    if the_username is None:
        msg = "Unknown username!"
        emit("for_invalid_username", msg)
    else:
        db.update_role(assigned_username, assigned_role)

        msg = "Role assigned successfully!"
        emit("for_valid_username", msg)


# -----------------------------------------------------------------------------------------


@socketio.on("remove_user")
def remove_user(username_inputted):

    the_username = db.get_user(username_inputted)  # check username in db

    if the_username is None:
        msg = "Unknown username!"
        emit("invalid_username", msg)
    else:
        db.delete_user(username_inputted)

        msg = "User removed successfully!"
        emit("valid_username", msg)