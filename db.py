'''
db
database file, containing all the logic to interface with the sql database
'''

# store data remotely, directly interact with the database in python
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import Session
from models import *
from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path
import os

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str, salt: str):
    with Session(engine) as session:
        user = User(username=username, password=password, salt=salt)
        session.add(user)
        session.commit()


# -----------------------------------------------------------------------------------------


# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)
    

# -----------------------------------------------------------------------------------------

# REF for sql query:
'''
USYD CODE CITATION ACKNOWLEDGEMENT
I declare that the following lines of code have been taken from the
website titled: "Difference between filter and filter_by in SQLAlchemy"
Original URL
https://stackoverflow.com/questions/2128505/difference-between-filter-and-filter-by-in-sqlalchemy
Last access April, 2024
'''

# gets salt from the database
def get_salt(username: str):
    with Session(engine) as session:
        db_salt = (
            session.query(User)
            .filter(User.username == username) # to find the salt associated with THE username
            .first()
        )
        if db_salt is not None:
            return db_salt.salt  # not returning session.get() since dealing with SQL, not with session
        return None


# -----------------------------------------------------------------------------------------


def get_password(username: str):
    with Session(engine) as session:
        user_pw = (
            session.query(User)
            .filter(User.username == username)
            .first()
        )
        if user_pw is not None:
            return user_pw.password
        return None


# -----------------------------------------------------------------------------------------


ENCRYPTION_KEY_FILE = 'CERTIFICATES/encryption.key'

# -- FOR ENCRYPTING FRIEND'S USERNAME -- 
# to ensure the encryption key remained consistent AT ALL TIMES
'''
USYD CODE CITATION ACKNOWLEDGEMENT
I declare that the following lines of code have been taken from the
website titled: "Encrypt and Decrypt Files using Python"
Original URL
https://www.geeksforgeeks.org/encrypt-and-decrypt-files-using-python/
Last access April, 2024
'''
def get_encryption_key():
    if not os.path.exists(ENCRYPTION_KEY_FILE):
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        return key
    else:
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()


# -----------------------------------------------------------------------------------------


# global encryption key
encryption_key = get_encryption_key()  

# insert a friend to the database
def insert_friend(sender: str, friend: str):
    with Session(engine) as session:
        # decrypt encrypted usernames for comparison
        key_value = Fernet(encryption_key)
        # friend_in_bytes = key_value.decrypt(friend)
        # decrypted_friend = friend_in_bytes.decode()
        decrypted_friend = key_value.decrypt(friend).decode()
        existing_friendship = (
            session.query(Friend)
            .filter(Friend.sender == sender, Friend.friend == decrypted_friend)
            .first()
        )
        if existing_friendship:
            return  # skip since alr in database

        sender_user = (
            session.query(User)
            .filter_by(username = sender)
            .one()  # to get that EXACTLY one
        )
        friend_user = (
            session.query(User)
            .filter_by(username = decrypted_friend)
            .one()
        )
        sender_friend = Friend(sender=sender, friend=friend, status="default")  # set default status in db
        session.add(sender_friend)
        session.commit()


# -----------------------------------------------------------------------------------------


# gets received friend requests
def get_received_requests(username: str):
    with Session(engine) as session:
        sent_requests = (
            session.query(Friend)
            .filter(Friend.status == "default")
            .all()
        )
        decrypted_ls = []
        key_value = Fernet(encryption_key)
        for sent_friend in sent_requests:
            decrypted_friend = key_value.decrypt(sent_friend.friend).decode()
            if decrypted_friend == username:  # compare with the decrypted friend
                decrypted_ls.append(sent_friend.sender)
        return decrypted_ls


# -----------------------------------------------------------------------------------------


# gets sent friend requests
def get_sent_requests(username: str):
    with Session(engine) as session:
        received_requests = (
            session.query(Friend)
            # just need to get ALL the friend he sent
            .filter(Friend.sender == username) 
            .all()
        )
        decrypted_ls = []  # because we dunno how many friends are sent request & we wanna include all of them
        key_value = Fernet(encryption_key)
        for sent_friends in received_requests:
            decrypted_friend = key_value.decrypt(sent_friends.friend).decode()
            decrypted_ls.append(decrypted_friend)
        return decrypted_ls  
        # return [request.friend for request in received_requests]


# -----------------------------------------------------------------------------------------


def for_add_friend(username: str):
    with Session(engine) as session:
        received_requests = (
            session.query(Friend)
            .filter(Friend.sender == username)
            .all()
        )
        decrypted_usernames = []
        key_value = Fernet(encryption_key)  # symmetric encryption
        for request in received_requests:
            '''
            USYD CODE CITATION ACKNOWLEDGEMENT
            I declare that the following lines of code have been taken from the
            website titled: "Unable to Except cryptography.fernet.InvalidToken Error in Python"
            Original URL
            https://stackoverflow.com/questions/60912944/unable-to-except-cryptography-fernet-invalidtoken-error-in-python
            Last access April, 2024
            '''
            try:
                decrypted_username = key_value.decrypt(request.friend).decode()
                # decode() -> convert from bytes to string datatype & then decrypt
                decrypted_usernames.append(decrypted_username)
            except (InvalidToken, TypeError):
                pass
        return decrypted_usernames  
        # return [request.friend for request in received_requests]


# -----------------------------------------------------------------------------------------


# for cases when the friend request is one-way request
def another_approved_request(username: str):
    with Session(engine) as session:
        received_requests = (
            session.query(Friend)
            .filter(Friend.status == "approve") # get all approved records
            .all()
        )
        decrypted_ls = []
        key_value = Fernet(encryption_key)
        for approved_friends in received_requests:
            # get all the Friend.friend that are approved
            decrypted_friend = key_value.decrypt(approved_friends.friend).decode()
            # check if the username is been approved in Friend.friend
            if username == decrypted_friend:
                # get the sender and return 
                decrypted_ls.append(approved_friends.sender)
        return decrypted_ls 


# -----------------------------------------------------------------------------------------


# gets approved friend requests
def get_approved_request(username: str):
    with Session(engine) as session:
        received_requests = (
            session.query(Friend)
            .filter(Friend.sender == username, Friend.status == "approve")
            .all()
        )
        decrypted_ls = []
        decrypted_friend = None
        key_value = Fernet(encryption_key)
        for approved_friends in received_requests:
            decrypted_friend = key_value.decrypt(approved_friends.friend).decode()
            decrypted_ls.append(decrypted_friend)

        if decrypted_friend == username:
            decrypted_ls.append(decrypted_friend)
        return decrypted_ls  
        # return [request.friend for request in received_requests]
    

# -----------------------------------------------------------------------------------------


# ---  AFTER ENCRYPTION for update friend request status ---
def update_request_status(sender_username: str, friend_username: str, status: str):
    with Session(engine) as session:
        key_value = Fernet(encryption_key)

        # from Test01 view
        # for Friend.sender ( eg. Test01 | lyvia(encrypted) | default )
        sent_friendships = (
            session.query(Friend)
            .filter(Friend.sender == sender_username)
            .all()
        )
        for friendship in sent_friendships:
            decrypted_friend = key_value.decrypt(friendship.friend).decode()
            if decrypted_friend == friend_username:  # match friend column
                friendship.status = status
        
        # from lyvia view
        # for Friend.sender ( eg. lyvia | Test01(encrypted) | default )
        receiver_friendship = (
            session.query(Friend)
            .filter(Friend.sender == friend_username)
            .all()
        )
        for friendship in receiver_friendship:
            decrypted_friend = key_value.decrypt(friendship.friend).decode()
            if decrypted_friend == sender_username:
                friendship.status = status

        # update 2 rows in db at the same time
        # ex: when Test01 (logged in) received lyvia's request & 
        #     Test01 approved lyvia, the request(s) of: 
        #     lyvia -> Test01 is approved
        #     Test01 -> lyvia is approved
        session.commit()


# -----------------------------------------------------------------------------------------


# insert message records into database with encrypted messages
def insert_encrypted_msg(room_id: int, username: str, receiver: str, encrypted_msg: str):
    with Session(engine) as session:
        chatroom = Chatroom(room_id=room_id, username=username, receiver=receiver, encrypted_msg=encrypted_msg)
        session.add(chatroom)
        session.commit()


# -----------------------------------------------------------------------------------------

'''
USYD CODE CITATION ACKNOWLEDGEMENT
I declare that the following lines of code have been taken from the
website titled: 
- "Using OR in SQLAlchemy"
- "SQLAlchemy 2.0 Documentation"
Original URL
- https://stackoverflow.com/questions/7942547/using-or-in-sqlalchemy
- https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.and_
Last access April, 2024
'''
# gets message history
def get_encrypted_msg(username: str, receiver: str):
    with Session(engine) as session:
        msg_history = (
            session.query(Chatroom)
            # .filter(Chatroom.room_id == room_id)
            # GETTING MSG THAT MATCHES THE USERNAME AND RECEIVER
            .filter(
                or_(
                    and_(Chatroom.username == username, Chatroom.receiver == receiver), 
                    and_(Chatroom.username == receiver, Chatroom.receiver == username)
                )
            )
            .all()
        )
        history_ls = []
        for msg in msg_history:
            history_ls.append((msg.username, msg.encrypted_msg))
        return history_ls
    

# -----------------------------------------------------------------------------------------


# gets message history
def get_db_roomID(room_id: str):
    with Session(engine) as session:
        roomID_in_db = (
            session.query(Chatroom)
            .filter(Chatroom.room_id == room_id)
            .first()
        )
        return roomID_in_db