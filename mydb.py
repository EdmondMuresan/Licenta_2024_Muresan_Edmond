from pymongo import MongoClient
import bcrypt
import io 
from PIL import Image
from datetime import datetime
class ChatRiseDB:
    client = MongoClient("localhost", 27017) 
    db = client.chatrise
    users = db.users
    events=db.events
    def insert_user(self, fullname, email, password,image_file):
        with open(image_file, 'rb') as f:
            image_data = f.read()
        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Use class variable ChatRiseDB.users
        ChatRiseDB.users.insert_one({
            "fullname": fullname,
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "image":image_data
        })

    def login_user(self, email, password):
        print("Logging in the user")
        user = ChatRiseDB.users.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            print("Login successful")
            return True
        else:
            print("Login failed. User not found or incorrect password.")
            return False
    def getinfo(self,email):
        user = ChatRiseDB.users.find_one({"email": email})
        print(user)
        return user
    def insert_event(self, userid,event_name,event_nr,event_location,event_theme,event_date,event_time):
        ChatRiseDB.events.insert_one({
            "userid":userid,
            "event_name":event_name,
            "event_nr":event_nr,
            "event_location":event_location,
            "event_theme":event_theme,
            "event_date":event_date,
            "event_time":event_time,
            "participants":[],
            "messages":[]
        })
    def get_events(self):
        events=ChatRiseDB.events.find()
        return events
    def connect_to_event(self,eventid,userid,use_case):
        event=ChatRiseDB.events.find_one({"_id":eventid})
        if event["userid"]==userid:
            return False
        for participant in event["participants"]:
            if participant["participantid"]==userid:
                return False
        if use_case=="join":
            ChatRiseDB.events.update_one({"_id":eventid},{"$push":{"participants":{"participantid":userid}}})
            return True
        else:
            return True
    def insert_message(self,userid,eventid,message):
        timestamp = datetime.now()
        ChatRiseDB.events.update_one(
        {"_id": eventid},
        {"$push": {"messages": {"userid": userid, "message": message, "timestamp": timestamp}}}
    )
    def get_messages(self,eventid):
        messages=ChatRiseDB.events.find_one({"_id":eventid})["messages"]
        return messages