'''
db
database file, containing all the logic to interface with the sql database
'''

# store data remotely, directly interact with the database in python
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import Session
from models import *
# from cryptography.fernet import Fernet, InvalidToken
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

# inserts a STUDENT to the database
def insert_user(username: str, role: str, password: str, salt: str):
    with Session(engine) as session:
        user = User(username=username, role=role, password=password, salt=salt, is_muted='false')
        session.add(user)
        session.commit()


# # inserts a STAFF to the database
# def insert_staff(username: str, role: str, password: str, salt: str):
#     with Session(engine) as session:
#         staff = Staff(username=username, role=role, password=password, salt=salt)
#         session.add(staff)
#         session.commit()


# -----------------------------------------------------------------------------------------


# gets a STUDENT from the database
def get_user(username_s: str):

    # IF ONLINE FRIEND(S) IS SELECTED FROM FRIENDLIST
    # to handle 2 ways of entering chatroom
    # either table > home (chat)  OR  friendlist > home (chat)
    if username_s:
        username = username_s.split(',')  # for more than 1 friends in chatroom
        with Session(engine) as session:
            for names in username:
                return session.get(User, names)


# -----------------------------------------------------------------------------------------


# gets user_id from the database
def get_user_id(username: str):
    with Session(engine) as session:
        user_id = (
            session.query(User)
            .filter(User.username == username)
            .first()
        )
        return user_id.user_id
    


def get_role(username: str):
    with Session(engine) as session:
        user = (
            session.query(User)
            .filter(User.username == username)
            .first()
        )
        if user.role == "Admin" or \
            user.role == "Academics" or \
            user.role == "Administrative staff":
            role = "staff"
        else:
            role = 'student'
        return user.role
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
        user_salt = (
            session.query(User)
            .filter(User.username == username) # to find the salt associated with THE username
            .first()
        )
        # staff_salt = (
        #     session.query(Staff)
        #     .filter(Staff.username == username) 
        #     .first()
        # )
        if user_salt is not None:
            return user_salt.salt  # not returning session.get() since dealing with SQL, not with session
        # if staff_salt is not None:
        #     return staff_salt.salt
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

def get_encryption_key():
    if not os.path.exists(ENCRYPTION_KEY_FILE):
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        return key
    else:
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
'''

# -----------------------------------------------------------------------------------------


# global encryption key
# encryption_key = get_encryption_key()  

# insert a friend to the database
def insert_friend(sender: str, friend: str):
    with Session(engine) as session:
        # decrypt encrypted usernames for comparison
        # key_value = Fernet(encryption_key)
        # friend_in_bytes = key_value.decrypt(friend)
        # decrypted_friend = friend_in_bytes.decode()
        # decrypted_friend = key_value.decrypt(friend).decode()
        existing_friendship = (
            session.query(Friend)
            .filter(Friend.sender == sender, Friend.friend == friend)
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
            .filter_by(username = friend)
            .one()
        )
        sender_friend = Friend(sender=sender, friend=friend, status="default")  # set default status in db
        session.add(sender_friend)
        session.commit()


# -----------------------------------------------------------------------------------------


def delete_user(username: str, friend: str):
    # print(f"-------------- db ------------------ {username} , {friend}")

    with Session(engine) as session:
        delete_friends = (
            session.query(Friend)
            .filter(
                or_(
                    and_(Friend.sender == username, Friend.friend == friend), 
                    and_(Friend.sender == friend, Friend.friend == username)
                )
            ) .all()
        )
        if delete_friends:
            # key_value = Fernet(encryption_key)
            for sent_friend in delete_friends:
                # decrypted_friend = key_value.decrypt(sent_friend.friend).decode()
                # if sent_friend.friend == friend:
                session.delete(sent_friend)
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
        # key_value = Fernet(encryption_key)
        for sent_friend in sent_requests:
            # decrypted_friend = key_value.decrypt(sent_friend.friend).decode()
            if sent_friend.friend == username:  # compare with the decrypted friend
                each_role = get_role(sent_friend.friend)
                decrypted_ls.append((sent_friend.sender, each_role))
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
        # key_value = Fernet(encryption_key)
        for sent_friends in received_requests:
            # decrypted_friend = key_value.decrypt(sent_friends.friend).decode()
            each_role = get_role(sent_friends.friend)
            decrypted_ls.append((sent_friends.friend, each_role))
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
        # key_value = Fernet(encryption_key)  # symmetric encryption
        for request in received_requests:
            '''
            USYD CODE CITATION ACKNOWLEDGEMENT
            I declare that the following lines of code have been taken from the
            website titled: "Unable to Except cryptography.fernet.InvalidToken Error in Python"
            Original URL
            https://stackoverflow.com/questions/60912944/unable-to-except-cryptography-fernet-invalidtoken-error-in-python
            Last access April, 2024
            '''
            # try:
                # decrypted_username = key_value.decrypt(request.friend).decode()
                # decode() -> convert from bytes to string datatype & then decrypt
            decrypted_usernames.append(request.friend)
            # except (InvalidToken, TypeError):
                # pass
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
        # key_value = Fernet(encryption_key)
        for approved_friends in received_requests:
            # get all the Friend.friend that are approved
            # decrypted_friend = key_value.decrypt(approved_friends.friend).decode()
            # check if the username is been approved in Friend.friend
            if username == approved_friends.friend:
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
        # decrypted_friend = None
        # key_value = Fernet(encryption_key)
        for approved_friends in received_requests:
            # decrypted_friend = key_value.decrypt(approved_friends.friend).decode()
            decrypted_ls.append(approved_friends.friend)

            if approved_friends.friend == username:
                decrypted_ls.append(approved_friends.friend)
        return decrypted_ls  
        # return [request.friend for request in received_requests]
    

# -----------------------------------------------------------------------------------------


# ---  AFTER ENCRYPTION for update friend request status ---
def update_request_status(sender_username: str, friend_username: str, status: str):
    with Session(engine) as session:
        # key_value = Fernet(encryption_key)

        # from Test01 view
        # for Friend.sender ( eg. Test01 | lyvia(encrypted) | default )
        sent_friendships = (
            session.query(Friend)
            .filter(Friend.sender == sender_username)
            .all()
        )
        for friendship in sent_friendships:
            # decrypted_friend = key_value.decrypt(friendship.friend).decode()
            if friendship.friend == friend_username:  # match friend column
                friendship.status = status
        
        # from lyvia view
        # for Friend.sender ( eg. lyvia | Test01(encrypted) | default )
        receiver_friendship = (
            session.query(Friend)
            .filter(Friend.sender == friend_username)
            .all()
        )
        for friendship in receiver_friendship:
            # decrypted_friend = key_value.decrypt(friendship.friend).decode()
            if friendship.friend == sender_username:
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
    
    # print(f'-++++++++++++++++++++++++++ {room_id}: int, {username}: str, {receiver}: str, {encrypted_msg}')

    with Session(engine) as session:
        chatroom = Chatroom(room_id=room_id, sender=username, receiver=receiver, encrypted_msg=encrypted_msg, is_read='read')
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

    # print(f"=================== in get encrypted msg -- {username} , {receiver}")

    if isinstance(username, str) and isinstance(receiver, str):
        with Session(engine) as session:
            msg_history = (
                session.query(Chatroom)
                # .filter(Chatroom.room_id == room_id)
                # GETTING MSG THAT MATCHES THE USERNAME AND RECEIVER
                .filter(
                    or_(
                        and_(Chatroom.sender == username, Chatroom.receiver == receiver), 
                        and_(Chatroom.sender == receiver, Chatroom.receiver == username)
                    )
                ).all()
            )
            history_ls = []
            for msg in msg_history:
                history_ls.append((msg.sender, msg.encrypted_msg))
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
    

# -----------------------------------------------------------------------------------------

    
# def get_notification(username: str, receiver: str):

#     visited = False
#     # get the list of unread msg for notification based on the logged in user
#     with Session(engine) as session:
#         unread_msg = (
#             session.query(Chatroom)
#             .filter(Chatroom.receiver == username)
#             .all()
#         )

#         unread_senders = []
#         for data in unread_msg:

#             # print(f"for looooooop -- {data.sender}, {data.receiver}")
#             if data.is_read == 'unread':  # get only the unread ones

#                 # skip duplicated senders
#                 if not data.sender in unread_senders:
#                     # print(f'hereeeeeeeeeeee -- {data.sender}, {data.receiver}')
                    
#                     # these messages are yet to be read
#                     unread_senders.append(data.sender)
#                     visited = True
            
#             else:  # nothing is unread
#                 return None  # if all the msg are read, return none
        
#         if not visited:
#             unread_from_MORE = (
#                 session.query(Chatroom)
#                 .filter(Chatroom.sender == username,
#                         Chatroom.is_read == 'unread')
#                 .all()
#             )

#             for MORE_receiver in unread_from_MORE:
#                 # print(f"sender == {MORE_receiver.sender} , receiver == {MORE_receiver.receiver}")
#                 # MORE_receiver_split = MORE_receiver.receiver.split(",")
#                 # print(f"split receiver ++ {MORE_receiver.receiver}")

#                 # if MORE_receiver_split == more_than_one_receiver:
#                 unread_senders.append(MORE_receiver.receiver)
#                 visited = True
#     # print(unread_senders)
#     return unread_senders





# def update_is_read(username: str, receiver: str):

#     # -- for ONLY ONE receiver --
#     with Session(engine) as session:
#         unread_from_ONE = (
#             session.query(Chatroom)
#             .filter(Chatroom.sender == receiver,
#                     Chatroom.receiver == username, 
#                     Chatroom.is_read == 'unread')
#             .all()
#         )
#         for ONE_receiver in unread_from_ONE:
#             # print(f'friend returned from SQL -- {ONE_receiver.receiver}')
#             ONE_receiver.is_read = 'read'
            
#         # -- for MORE THAN 1 receiver --
#         more_than_one_receiver = receiver.split(",")
#         # for the_friend in more_than_one_receiver:
#         #     print(f"more than one receiver -- {more_than_one_receiver}")

#         unread_from_MORE = (
#             session.query(Chatroom)
#             .filter(Chatroom.sender == username,
#                     Chatroom.is_read == 'unread')
#             .all()
#         )

#         for MORE_receiver in unread_from_MORE:
#             # print(f"sender == {MORE_receiver.sender} , receiver == {MORE_receiver.receiver}")
#             MORE_receiver_split = MORE_receiver.receiver.split(",")
#             # print(f"split receiver ++ {MORE_receiver_split}")

#             if MORE_receiver_split == more_than_one_receiver:
#                 # print(f"testing here -- {MORE_receiver.receiver}")
#                 MORE_receiver.is_read = 'read'
#         session.commit()



# def get_notification(username: str, receiver: str):
#     with Session(engine) as session:
#         # get the list of unread msg based on the logged-in user
#         unread_msg = (
#             session.query(Chatroom)
#             .filter(
#                 or_(Chatroom.receiver == username,
#                     Chatroom.receiver.like(f"%{username}%")))
#             .all()
#         )

#         unread_senders = []
#         for data in unread_msg:
#             if data.is_read == 'unread' and not data.sender in unread_senders:  # get only the unread ones
#                 # these messages are yet to be read
#                 unread_senders.append(data.sender)
#         if len(unread_senders) == 0:
#             return None
#         else: 
#             return unread_senders


def update_is_read(username: str, receiver: str):

#  in update is read -- Test01 , {'jQuery364038394677790519881': {'events': {'keyup': [{'type': 'keyup', 'origType': 'keyup', 'guid': 2, 'namespace': ''}]}}}
    with Session(engine) as session:
        
        # -- for ONLY ONE receiver --
        unread_from_ONE = (
            session.query(Chatroom)
            .filter(Chatroom.sender == receiver,
                    Chatroom.receiver == username, 
                    Chatroom.is_read == 'unread')
            .all()
        )
        # print("ONEEEEEEreceiver")
        for ONE_receiver in unread_from_ONE:
            # print(f"ONEEEEEEEEEEEEEEE_receiver -- {ONE_receiver.sender} , {ONE_receiver.encrypted_msg}")
            ONE_receiver.is_read = 'read'
        session.commit()
        
        # -- for MORE THAN 1 receiver --
        more_than_one_receiver = receiver.split(",")
        for the_receiver in more_than_one_receiver:
            unread_from_MORE = (
                session.query(Chatroom)
                .filter(Chatroom.sender == the_receiver,
                        Chatroom.receiver.like(f"%,{username}%") | Chatroom.receiver.like(f"%{username},%") | Chatroom.receiver.like(f"{username}"),
                        Chatroom.is_read == 'unread')
                        # Chatroom.receiver == username, 
                .all()
            )
            # print(f"MOREEEEEEreceiver == {the_receiver} , {username}")
            for MORE_receiver in unread_from_MORE:
                # print(f"MOREEEEEEEEEEEEEEEE_receiver -- {MORE_receiver.sender} , {MORE_receiver.encrypted_msg}")
                
                MORE_receiver.is_read = 'read'
            session.commit()


def get_notification(username: str):

    with Session(engine) as session:
        # consider ALL cases of receivers 
        unread_messages = (
            session.query(Chatroom)
            .filter(Chatroom.receiver.like(f"%,{username}%") | 
                    Chatroom.receiver.like(f"%{username},%") | 
                    Chatroom.receiver.like(f"{username}"))
            .all()
        )

        chat_dict = {}
        single_counter = 0
        group_counter = 0
        group_friend = None

        if unread_messages:
            for data in unread_messages:
                if data.is_read == 'unread': 
                    if not ',' in data.receiver: 
                        chat_type = "single"
                    else:
                        chat_type = "group"

                    if (data.sender, chat_type, data.receiver) not in chat_dict:
                        chat_dict[(data.sender, chat_type, data.receiver)] = True

            # single_chat_counter = sum([1 for sender, chat_type in chat_dict if chat_type == "single"])
            # group_chat_counter = sum([1 for sender, chat_type in chat_dict if chat_type == "group"])
            for sender, type, receivers in chat_dict:
                
                if type == 'single':
                    single_counter += 1
                elif type == 'group':
                    group_counter += 1

                if receivers:
                    receiver_s = receivers.split(",")
                    for name in receiver_s:
                        if name != username:
                            group_friend = name
                            # print(f'62888888888888888 ===== {group_friend}')

            if len(chat_dict) > 0:
                # print(f"singleee chatttttt -- {chat_dict.keys()}, {group_counter}, {single_counter}, {group_friend}")
                return chat_dict.keys(), group_counter, single_counter, group_friend
            else:
                return None, None, None, None  # no unread message
        return None, None, None, None


# -----------------------------------------------------------------------------------------


def insert_new_article(username: str, user_id: int, role: str, title: str, content: str, post_private: str):
    # print(f"DBBBBBBBBB -- {username}, {role}, {title}, {content}, {post_private}")
    
    with Session(engine) as session:
        article = Article(username=username, user_id=user_id, role=role, title=title, content=content, post_private=post_private)
        session.add(article)
        session.commit()


def get_article():
    with Session(engine) as session:
        articles = (
            session.query(Article)
            .order_by(Article.article_id.desc())
            .all()
        )
        article_ls = []
        for article in articles:
            article_in_dict = {
                'article_id': article.article_id,
                'username': article.username,
                'user_id': article.user_id,
                'role': article.role,
                'title': article.title,
                'content': article.content,
                'post_private': article.post_private
            }
            article_ls.append(article_in_dict)
        return article_ls
    

# -----------------------------------------------------------------------------------------


def insert_new_comment(article_id: int, username: str, user_id: int, role: str, comment:str):
    with Session(engine) as session:
        new_comment = Comment(article_id=article_id, username=username, user_id=user_id, role=role, comment=comment)
        session.add(new_comment)
        session.commit()


def show_comment(article_id: int):
    with Session(engine) as session:
        comments = (
            session.query(Comment)
            .filter(Comment.article_id == article_id)
            .all()
        )
        comment_ls = []
        for comment in comments:
            comment_in_dict = {
                'username': comment.username,
                "user_id": comment.user_id,
                'role': comment.role,
                'comment': comment.comment
            }
            comment_ls.append(comment_in_dict)
        return comment_ls
    

# -----------------------------------------------------------------------------------------


def edit_article(article_id: int, title: str, content: str):
    # print(f"DBBBBBBBBB -- {username}, {user_id}, {role}, {title}, {content}")
    
    with Session(engine) as session:
        # filter by the article_id and username (to be safe)
        content_to_be_updated = (
            session.query(Article)
            .filter(Article.article_id == article_id)
            .first()
        )
        content_to_be_updated.title = title
        content_to_be_updated.content = content
        session.commit()


def get_selected_article(article_id: int):
    with Session(engine) as session:
        article = (
            session.query(Article)
            .filter(Article.article_id == article_id)
            .first()
        )
        if article is not None:
            article_in_dict = {
                'article_id': article.article_id,
                'username': article.username,
                'user_id': article.user_id,
                'role': article.role,
                'title': article.title,
                'content': article.content,
            }
            return article_in_dict
    

# -----------------------------------------------------------------------------------------


def delete_article(article_id: int):
    with Session(engine) as session:
        delete_article = (
            session.query(Article)
            .filter(Article.article_id == article_id)
            .first()
        )
        delete_comment = (
            session.query(Comment)
            .filter(Comment.article_id == article_id)
            .first()
        )
        if delete_article is not None:
            session.delete(delete_article)
            session.commit()

        if delete_comment is not None:
            session.delete(delete_comment)
            session.commit()


# -----------------------------------------------------------------------------------------


def delete_comment(comment_id: int):
    with Session(engine) as session:
        delete_comment = (
            session.query(Comment)
            .filter(Comment.comment_id == comment_id)
            .first()
        )
        if delete_comment is not None:
            session.delete(delete_comment)
            session.commit()


# -----------------------------------------------------------------------------------------


def get_comment_id(article_id: int, the_content: str):

    with Session(engine) as session:
        comments = (
            session.query(Comment)
            .filter(Comment.article_id == article_id)
            .all()
        )
        if comments:
            for comment in comments:
                if comment.comment == the_content:
                    return comment.comment_id
                

# -----------------------------------------------------------------------------------------


def get_is_muted(username: str):
    with Session(engine) as session:
        is_muted = (
            session.query(User)
            .filter(User.username == username)
            .first()
        )
        return is_muted.is_muted


def mute_user(mute_username: str):
    # print(f'in dbbbbbbbb - {mute_username}')

    with Session(engine) as session:
        user_to_mute = (
            session.query(User)
            .filter(User.username == mute_username)
            .first()
        )
        # print(user_to_mute.username)
        if user_to_mute:
            user_to_mute.is_muted = 'true'
            session.commit()


def unmute_user(unmute_username: str):
    # print(f" in dbbbbbbbbbbb - ----- {unmute_username}")
    with Session(engine) as session:
        user_to_unmute = (
            session.query(User)
            .filter(User.username == unmute_username)
            .first()
        )
        if user_to_unmute:
            user_to_unmute.is_muted = 'false'
            session.commit()


# -----------------------------------------------------------------------------------------


def update_role(the_username: str, the_role: str):
    # print(f'in dbbbbbbbb - {the_username} -- {the_role}')

    with Session(engine) as session:
        valid_username = (
            session.query(User)
            .filter(User.username == the_username)
            .first()
        )
        if the_role == "Student":
            the_role = "student"
        
        if valid_username:
            valid_username.role = the_role
            session.commit()


# -----------------------------------------------------------------------------------------


def delete_user(username_inputted: str):
    with Session(engine) as session:
        delete_user = (
            session.query(User)
            .filter(User.username == username_inputted)
            .first()
        )
        if delete_user is not None:
            session.delete(delete_user)
            session.commit()
