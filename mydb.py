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
    def leave_event(self,eventid,userid):
        ChatRiseDB.events.update_one({"_id":eventid},{"$pull":{"participants":{"participantid":userid}}})
    def get_user_name(self,userid):
        user=ChatRiseDB.users.find_one({"_id":userid})
        return user["fullname"]
    def delete_user(self,userid):
        ChatRiseDB.users.delete_one({"_id":userid})
        for event in ChatRiseDB.events.find():
            if event["userid"]==userid:
                ChatRiseDB.events.delete_one({"_id":event["_id"]})
            for participant in event["participants"]:
                if participant["participantid"]==userid:
                    ChatRiseDB.events.update_one({"_id":event["_id"]},{"$pull":{"participants":{"participantid":userid}}})
    def check_password(self,id,password):
        user=ChatRiseDB.users.find_one({"_id":id})
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return True
        else:
            return False
    def update_user(self,userid,fullname,email,image_file):
        with open(image_file, 'rb') as f:
            image_data = f.read()  
        ChatRiseDB.users.update_one({"_id":userid},{"$set":{"fullname":fullname,"email":email,"image":image_data}})
    def get_members(self,eventid):
        members=ChatRiseDB.events.find_one({"_id":eventid})["participants"]
        member_elements={}
        for member in members:
            member_name=ChatRiseDB.users.find_one({"_id":member["participantid"]})["fullname"]
            member_elements[member["participantid"]]=member_name
        member_elements[ChatRiseDB.events.find_one({"_id":eventid})["userid"]]=self.get_user_name(ChatRiseDB.events.find_one({"_id":eventid})["userid"])+"  Admin"
        
        print(member_elements)
        return member_elements
    def leave_event(self,eventid,userid):
        ChatRiseDB.events.update_one({"_id":eventid},{"$pull":{"participants":{"participantid":userid}}})
    def admin_status(self,userid,eventid):
        event=ChatRiseDB.events.find_one({"_id":eventid})
        if event["userid"]==userid:
            return True
        else:
            return False
    def get_event_info(self,event_id):
        event=ChatRiseDB.events.find_one({"_id":event_id})
        return event
    def delete_event(self,event_id):
        ChatRiseDB.events.delete_one({"_id":event_id})
        print("Event Deleted")