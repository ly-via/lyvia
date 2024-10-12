'''
socket_routes
file containing all the routes related to socket.io
'''

import db, hashlib, hmac
from flask_socketio import join_room, emit, leave_room
from flask import request
from models import Room
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

room = Room()

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


'''
######  -- how public/private key generated with PKCS1_v1_5 --  ###### 

# for digital signature
# from Crypto.Signature import PKCS1_v1_5
# from Crypto.Hash import SHA256
# import codecs

# key = RSA.generate(1024)
# private_key = key.exportKey()
# public_key = key.publickey().exportKey()
# print(private_key)
# print(public_key)
'''

############ OAEP -- EN/DECRYPTING MSG all in py file ############

# private_key = """-----BEGIN RSA PRIVATE KEY-----
# MIICXAIBAAKBgQD3R2ufISIIgYH2wIZroL8gtgZbGtn1fyR0kU2RJ1LCMX38waRV
# L5nuHSYqXCl4QKktjSy9gzTavoh2rTZ0n7U0zHCn7qgs67uCY69aAkqe57JlTEER
# XIvnrPQf8/Ia/oh6J+upnfMlXe/qqXFetzyK/dA0jJI492M3ahmT7J3pAQIDAQAB
# AoGAUKb/T7IvVwXinVgzH6SY4jLshMePwpY7DjgcTBU+1W7uEEQadNxnQPZJ7fQM
# ZJf2dhB/QLqsQRJ3EPoy8jvrDk7kuLZbKBq31kKRIlzHl+JzTDk0q6lSx6mERIcn
# KGbau5HE5ayKppykGapOQ1vL2wAIIbdAkIWO6eZBYPAYelcCQQD6Cnp0B7QO/Ime
# ERXEu/TBadqGljdXz4ir1oBWDKGcrDGT+GaBHGBMViFMqWbEdfqLkNtuPizWKAUG
# 6KQ0TLSDAkEA/SwXWIgkhsfVonHs0HWew/k2/FcxTVM2kA9denxz/J3ymAdRNBrl
# Mp93NkEPKesHUx0IcPrFxf2H/gMF2LhdKwJAI/V30NH+yhz1aZ8JY2aod1xSygI2
# aVF2VUge4sEkSNTWuHIDw9Oh4biNR2ohVmWlJ4col30nk5Dj0C+K1d6mIwJAbxrf
# b/nnVcLzLWQj0mQb9dMz31AAkfe31Ub49h0R5cYHRdLIPz6iYTH8ZjHtDq9XOpFe
# N/7FtpsKCF6ZPT/DmwJBALX5ZYDwkU7RJurJFtcK7MuLc4ZRSpgJ8L6ykgjNJ6q4
# ItahB3LSNspRozkYKJdE6yAo9XA+EADLNfW96qkCZv0=
# -----END RSA PRIVATE KEY-----"""

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

def decrypt_msg(encrypted_msg, private_key):
    private_key_obj = RSA.importKey(private_key)
    cipher = PKCS1_OAEP.new(private_key_obj)
    # encrypted_message = b"z\x9b\x7f\xca\xbamrT0\x83\xb5\x17\xf1\xa2\x1e\x9eW\xbe n\xad\xf0\xa8\x1e#\xeb|\x8e\xcd\x8f\xb34\x9br\x04NaSI\x12<\xfd9|\xa0:IOa\x9b\x07\x1e\x8e_o\x81\x01\xaf!\xdcR\xfbU\xe3\xad\xe0\xf8b=,\x92\xbfn\x9d]1;p\xb1V\xe9\x02\xea9`\xb9\x03g\x99\xa9\xe5\x10\x18\xb6\xb8\xad\xc1\x92\x87}\x98'\xe2f?\x16\xba\xe5\x17!\x1ai|0r\x9e\xba\xbf\xb9\x99\xdf\xb9\xbfw.X\xb6\xbf" 
    decrypted_msg = cipher.decrypt(encrypted_msg)
    return decrypted_msg.decode()

def encrypt_msg(message, public_key):
    receiver_key = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(receiver_key)
    encrypted_msg = cipher.encrypt(message.encode())
    return encrypted_msg

# -----------------------------------------------------------------------------------------

def get_mac(username, receiver, room_id):
    # use user's password as the secret key
    user_pw = db.get_password(username)
    if not user_pw:
        return "Error with secret key: User not found!"
    encrypted_msg = db.get_encrypted_msg(username, receiver)  # in list type
    for msg in encrypted_msg:  # convert into string
        msg_in_str = ''.join([str(msg)])

    user_pw_in_bytes = user_pw.encode('utf-8')  # convert string into bytes
    mac = hmac.new(user_pw_in_bytes, msg_in_str.encode(), hashlib.sha256).hexdigest()
    return mac

def verify_mac(msg, received_mac, username):
    user_pw = db.get_password(username)
    user_pw_in_bytes = user_pw.encode('utf-8')
    mac = hmac.new(user_pw_in_bytes, msg.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(received_mac, mac)

# -----------------------------------------------------------------------------------------

@socketio.on("enter_chatroom")
def display_msg_history(room_id, username, receiver):
    print("Room ID: ", room_id)
    msg_history_ls = db.get_encrypted_msg(username, receiver)
    # get sender, encrypted msg from db for that room_id looping history_ls
    for sender, msg_history in msg_history_ls:
        private_key = get_private_key(filename)
        decrypted_msg_str = decrypt_msg(msg_history, private_key)
        # only emit and print the ones with actual msg history
        # to avoid printing empty message histories
        # it's a bad way to do it though :(
        if len(decrypted_msg_str) > 0:
            emit("incoming", (f"{sender}: {decrypted_msg_str}", "#a6a6a6"))

# -----------------------------------------------------------------------------------------

@socketio.on("send")
def send(username, receiver, message, room_id):
    # encrypt plaintext msg
    encrypted_msg = encrypt_msg(message, public_key)
    # insert into db with those data
    db.insert_encrypted_msg(room_id, username, receiver, encrypted_msg)
    # db.insert_encrypted_msg(room_id, username, message)
    private_key = get_private_key(filename)     # decrypt
    decrypted_msg = decrypt_msg(encrypted_msg, private_key)

    # HMAC - to authenticate ALL msg
    # use ALL msg to generate & verify HMAC
    db_encrypted_msg = db.get_encrypted_msg(username, receiver)
    for msg in db_encrypted_msg:
        msg_in_str = ''.join([str(msg)])

    mac = get_mac(username, receiver, room_id)
    is_valid_mac = verify_mac(msg_in_str, mac, username)
    # is_valid_mac = verify_mac(decrypted_msg, mac, username)
    if not is_valid_mac:
        print("ALERT! ALERT! ALERT! MAC verification failed!!!")
        return "ALERT! ALERT! ALERT! MAC verification failed!!!"
    emit("incoming", (f"{username}: {decrypted_msg}", mac), to=room_id)

# -- EXAMPLE USAGE -- 
# message = "Hello, this is a secret message!"
# private_key = get_private_key(filename)
# encrypted_msg = encrypt_msg(message, public_key)
# msg = decrypt_msg(encrypted_msg, private_key)
# print(msg)

################# EN/DECRYPTING MSG all in py file ^ ##################


# -----------------------------------------------------------------------------------------

# sent when the user joins a room
# join room event handler
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
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
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        return room_id

    # if the user isn't inside of any room, create a new room 
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# -----------------------------------------------------------------------------------------

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)
