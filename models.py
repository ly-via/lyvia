'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Dict
import db

# data models
class Base(DeclarativeBase):
    pass

# model to store user information
class User(Base):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[str] = mapped_column(String)
    salt: Mapped[str] = mapped_column(String)
    
# -----------------------------------------------------------------------------------------

# model to store friend information
class Friend(Base):
    __tablename__ = "friend"
    sender: Mapped[str] = mapped_column(String, ForeignKey('user.username'))
    friend: Mapped[str] = mapped_column(String, ForeignKey('user.username'))
    status : Mapped[str] = mapped_column(String)

    # add constraints 
    '''
    USYD CODE CITATION ACKNOWLEDGEMENT
    I declare that the following lines of code have been taken from the
    website titled: "SQLAlchemy: Possible to declare a column as primary key declaratively?"
    Original URL
    https://stackoverflow.com/questions/25749803/sqlalchemy-possible-to-declare-a-column-as-primary-key-declaratively
    Last access April, 2024
    '''
    __table_args__ = (
        PrimaryKeyConstraint('sender', 'friend'),
    )

# -----------------------------------------------------------------------------------------

# OnlineUser class, used to keep track of which user is online
'''
USYD CODE CITATION ACKNOWLEDGEMENT
I declare that the following lines of code have been taken from the
website titled: "How to Make a Chat Application in Python"
Original URL
https://thepythoncode.com/article/make-a-chat-room-application-in-python
Last access April, 2024
'''
class OnlineUser():
    def __init__(self):
        self.online_user = set()

    def set_online(self, user: str):
        self.online_user.add(user)

    def set_offline(self, user: str):
        if user in self.online_user:
            self.online_user.remove(user)

    def is_online(self, user: str) -> bool:
        return user in self.online_user

# -----------------------------------------------------------------------------------------

# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# -----------------------------------------------------------------------------------------

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}
        # to set user as "Online" when they logged in
        self.online_user = OnlineUser()

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        while db.get_db_roomID(str(room_id)):
            room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
        # return self.dict.get(user)
    
    def set_online(self, user: str):
        self.online_user.set_online(user)

    def set_offline(self, user: str):
        self.online_user.set_offline(user)

    def is_online(self, user: str) -> bool:
        return self.online_user.is_online(user)

# -----------------------------------------------------------------------------------------

class Chatroom(Base):
    __tablename__ = "chatroom"
    '''
    USYD CODE CITATION ACKNOWLEDGEMENT
    I declare that the following lines of code have been taken from the
    website titled: "unable to create autoincrementing primary key with flask-sqlalchemy"
    Original URL
    https://stackoverflow.com/questions/20848300/unable-to-create-autoincrementing-primary-key-with-flask-sqlalchemy    Last access April, 2024
    '''
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(Integer)
    username: Mapped[str] = mapped_column(String)
    receiver: Mapped[str] = mapped_column(String)
    encrypted_msg: Mapped[str] = mapped_column(String)