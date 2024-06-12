from mydb import ChatRiseDB
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRoundFlatButton,MDFillRoundFlatButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget ,ThreeLineRightIconListItem,MDList
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from datetime import datetime
from kivymd.uix.pickers import MDDatePicker,MDTimePicker
from PIL import Image
import io
from kivy.clock import Clock
user={}
current_chat_room=None
reload=None
class AllertDialog():
    dialog=None
    def show_alert_dialog(self,info):
        self.dialog = MDDialog(
            title="Caution!",
            text=info,
            buttons=[
                MDRoundFlatButton(
                    text="Ok",
                    text_color="orange",
                    on_release = self.close_dialog
                    ),
                ]
            )
        self.dialog.open()
    def kick_dialog(self,info,event_id,user_id):
            self.dialog = MDDialog(
                title="Caution!",
                text="Would you like to kick "+info,
                buttons=[
                    MDRoundFlatButton
                    (
                        text="Yes",
                        text_color="orange",
                        on_release = lambda x, n_event_id=event_id, n_user_id=user_id:self.kick(n_event_id,n_user_id)
                    ),
                    MDRoundFlatButton
                    (
                        text="Cancel",
                        text_color="orange",
                        on_release = self.close_dialog
                    )
                ]
            )
            self.dialog.open()
    def close_dialog(self,obj):
        self.dialog.dismiss()
    def kick(self,event_id,user_id):
        print("Trying to kick")
        db.leave_event(event_id,user_id)
        self.close_dialog(self.dialog)
class EventDetails(AllertDialog):
    def show_info_dialog(self,title,info,event_id,user_id,use_case):
        global current_chat_room
        current_chat_room=event_id
        self.new_text=None
        if db.admin_status(user["_id"],event_id):
            self.new_text="Delete event"
        else:
            self.new_text="Leave"
        print(event_id)
        if use_case=="join":
            self.dialog = MDDialog(
                title=title,
                text=info,
                buttons=[
                    MDRoundFlatButton(
                        text="Join",
                        theme_text_color= "Custom",
                        text_color="orange",
                        on_release=lambda x, event_id=event_id, user_id=user_id: self.connect_to_event(event_id, user_id)
                    ),
                    MDRoundFlatButton(
                        text="Cancel",
                        text_color="orange",
                        on_release = self.close_dialog
                        )
                ]
                        )
            
        elif use_case=="message":
            self.dialog = MDDialog(
            title=title,
            text=info,
            buttons=[    
                MDRoundFlatButton(
                        text="Enter",
                        text_color="orange",
                        on_release=lambda x, event_id=event_id, user_id=user_id: self.change_room(event_id))
                ,
                MDRoundFlatButton(
                        text=self.new_text,
                        text_color="orange",
                        on_release = lambda x, event_id=event_id, user_id=user_id: self.leave_room(event_id,user_id,self.new_text)
                        ),
                MDRoundFlatButton(
                        text="Cancel",
                        text_color="orange",
                        on_release = self.close_dialog
                        )
                ]
            )
        self.dialog.open() 
    def change_room(self,event_id):
        print(event_id)
        self.close_dialog(self.dialog)
        app=MDApp.get_running_app()
        app.root.current="chatroom"
        
    def connect_to_event(self,event_id,user_id):
        self.close_dialog(self.dialog)
        if(db.connect_to_event(event_id,user_id,"join")):
            self.show_alert_dialog("Success")
        else:
            self.show_alert_dialog("Error")
            
    def leave_room(self,event_id,user_id, text):
        self.close_dialog(self.dialog)
        if text=="Delete event":
            db.delete_event(event_id)
            self.show_alert_dialog("Event deleted!")
        else:
            db.leave_event(event_id,user_id)
            self.show_alert_dialog("Chat room left!")
        
class Register(MDScreen,AllertDialog):
    dialog=None
    def register(self):
        fullname=self.ids.fullname.text
        email=self.ids.email.text
        password=self.ids.password.text
        fullname=fullname.strip()
        email=email.strip()
        password=password.strip()
        image=self.ids.my_image.source
        if(fullname=="" or email=="" or password=="" or image==""):
            self.show_alert_dialog("Invalid Credentials!")
        elif(db.getinfo(email)):
            self.show_alert_dialog("User exists,please login!")
        else:
            db.insert_user(fullname,email,password,image)
            app=MDApp.get_running_app()
            app.root.current="login"
            
            self.show_alert_dialog("User registered"+fullname)

    def selected(self,filename):
        try:
            self.ids.my_image.source=filename[0]
            file=filename[0]
            if file[-3:] in ["jpg","png"]: 
                pass
            else:
                self.show_alert_dialog("Invalid image format!")
        except:
            pass
class Login(MDScreen,AllertDialog):
    dialog=None
    def on_enter(self):
        print("Entering login")
        with open("user_data.txt","r") as file:
            data=file.read()
            if data:
                split_data=data.split(" ")
                if(db.login_user(split_data[0],split_data[1])):
                    global user
                    app=MDApp.get_running_app()
                    app.root.current="main"
                    user=db.getinfo(split_data[0])
                    print(str(user)+"Welcome")
                
    def login(self):
        global user
        email=self.ids.email.text
        password=self.ids.password.text
        self.ids.email.text=""
        self.ids.password.text=""
        checkbox=self.ids.remember_me
        if(db.login_user(email,password)):
            
            app=MDApp.get_running_app()
            app.root.current="main"
            user=db.getinfo(email)
            if checkbox.active:self.save_user_data(email,password)
            print(str(user)+"Welcome")
                
        else:
            self.show_alert_dialog("Invalid credentials!")
    def save_user_data(self,email,password):
        with open("user_data.txt","a") as file:
            data=str(email+ " " +password)
            file.write(data)   
class CreateChatRoom(MDScreen,AllertDialog):
    dialog=None
    def on_pre_enter(self, *args):
        theme_spinner = self.ids.theme_spinner
        theme_options = ["Sport", "Outdoor", "Gaming", "Meetup", "Studies"]
        theme_spinner.values = theme_options
        date_time=self.ids.date
        date_time.text=datetime.now().strftime("%Y-%m-%d")
    def on_save(self,instance,value,date_range):
        date_time=self.ids.date
        date_time.text=str(value)
        
    def show_date_picker(self):
        date_dialog=MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()
        
    def get_time(self,instance,mytime):
        time=self.ids.time
        time.text=str(mytime)
    def show_time_picker(self):
        time_dialog=MDTimePicker()
        time_dialog.bind(time=self.get_time)
        time_dialog.open()
    def get_desired_data(self):
        global user
        user_id=user['_id']
        event_name=self.ids.event_name.text
        try :
            event_nr=int(self.ids.event_nr.text)
        except ValueError:
            self.show_alert_dialog("Invalid data for number the value will be set to 15!")
            event_nr=15
        event_location=self.ids.location.text
        event_theme=self.ids.theme_spinner.text
        event_date=self.ids.date.text
        event_time=self.ids.time.text
        data=[]
        data.append(user_id)
        data.append(event_name)
        data.append(event_nr)
        data.append(event_location)
        data.append(event_theme)
        data.append(event_date)
        data.append(event_time)
        return data
    def create_event(self):
        data=self.get_desired_data()
        user_id=data[0]
        event_name=data[1]
        event_nr=data[2]
        event_location=data[3]
        event_theme=data[4]
        event_date=data[5]
        event_time=data[6]
        if event_name =="" or event_nr=="" or event_location=="" or event_theme=="Select Theme" or type(event_nr)!=int or event_nr>100 or event_nr<1:
            self.show_alert_dialog("Invalid data!")
        else:
            db.insert_event(user_id,event_name,event_nr,event_location,event_theme,event_date,event_time)
            app=MDApp.get_running_app()
            app.root.current="main"
            self.show_alert_dialog("Event created!")
    def on_leave(self):
        self.ids.event_name.text=""
        self.ids.event_nr.text=""
        self.ids.location.text=""
        self.ids.theme_spinner.text="Select Theme"
class MainPage(MDScreen,EventDetails):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_filter = 'Choose Event Filter'
        self.event_status = None
        self.event_attending = None
    def logout(self):
        global user
        user={}
        with open("user_data.txt","w") as file:
            file.write("")
        app=MDApp.get_running_app()
        app.root.current="login"
    def on_enter(self):
        global user
        self.ids.user_spinner.text=str(user["fullname"])
        image = Image.open(io.BytesIO(user['image']))
        image.save('user.png')
        self.ids.user_image.source="user.png"
        self.load_events(True,"join")
        Clock.schedule_interval(self.reload_events, 1)	
    def load_events(self,type,use_case,filter="Choose Event Filter"):
        global user
        events=db.get_events()
        list_view = MDList()
        for event in events:
            event_name=event["event_name"]
            event_location = event["event_location"]
            event_theme = event["event_theme"]
            event_time = event["event_time"]
            event_nr = int(event["event_nr"])
            event_date=event["event_date"]
            event_id=event["_id"]
            event_creator=db.get_user_name(event["userid"])
            if filter=="Choose Event Filter":
                if db.connect_to_event(event_id,user["_id"],"view")==type:
                    item = OneLineAvatarIconListItem(
                        IconLeftWidget(icon="human-capacity-increase"),
                        on_release=lambda x, eventid=event_id,loc=event_location, theme=event_theme, date=event_date, time=event_time, nr=event_nr, name=event_name: self.show_info_dialog(f"{name} ~~ Event details", f" Location:{loc} \n Theme:{theme} \n Date:{date} Time:{time} \n Available slots: {nr}/{nr-len(event['participants'])}" ,eventid,user["_id"],use_case),
                        
                        text=f"{event['event_name']} {event['event_date']} {event['event_time']} \n Event by {event_creator}",
                    )
                    print(event_name)
                    list_view.add_widget(item)
            elif filter==event_theme:
                if db.connect_to_event(event_id,user["_id"],"view")==type:
                    item = OneLineAvatarIconListItem(
                        
                        IconLeftWidget(icon="human-capacity-increase"),
                        on_release=lambda x, eventid=event_id,loc=event_location, theme=event_theme, date=event_date, time=event_time, nr=event_nr, name=event_name: self.show_info_dialog(f"{name} ~~ Event details", f" Location:{loc} \n Theme:{theme} \n Date:{date} Time:{time} \n Available slots: {nr}/{nr-len(event['participants'])}" ,eventid,user["_id"],use_case),
                        
                        text=f"{event['event_name']} {event['event_date']} {event['event_time']} \n Event by {event_creator}",

                    )
                    print(event_name)
                    list_view.add_widget(item)
        self.ids.event_box.add_widget(list_view)
    def change_mine(self):
        self.ids.event_box.clear_widgets()
        self.load_events(False,"message",self.event_filter)
        self.event_status=False
        self.event_attending="message"
    def change_not_mine(self):
        self.ids.event_box.clear_widgets()
        self.load_events(True,"join",self.event_filter)	
        self.event_status=True
        self.event_attending="join"
    def on_leave(self, *args):
        self.ids.event_box.clear_widgets()
        Clock.unschedule(self.reload_events)
    def user_action(self,action):
        if action=="Logout":
            self.logout()
        if action=="Delete User":
            self.delete_user()
        if action=="Edit User":
            app=MDApp.get_running_app()
            app.root.current="edituser"
    def filter_action(self,actionname):
        if actionname=="Sport":
            self.event_filter="Sport"
        if actionname=="Outdoor":
            self.event_filter="Outdoor"
        if actionname=="Gaming":
            self.event_filter="Gaming"
        if actionname=="Meetup":
            self.event_filter="Meetup"
        if actionname=="Studies":
            self.event_filter="Studies"
        if actionname=="Choose Event Filter":
            self.event_filter="Choose Event Filter"
        self.ids.event_box.clear_widgets()
        self.load_events(self.event_status,self.event_attending,self.event_filter)
    def delete_user(self):
        db.delete_user(user["_id"])
        self.show_alert_dialog("User deleted!")
        self.logout()
    def reload_events(self,*args):
        self.ids.event_box.clear_widgets()
        self.load_events(self.event_status,self.event_attending,self.event_filter)
    
class ChatRoom(MDScreen, EventDetails):
    print(current_chat_room)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.printed_messages = set()
    def get_all_members(self):
        self.ids.members.values = []
        self.members=db.get_members(current_chat_room)
        member_name_list=list(self.members.values())
        print(type(self.members))
        global user
        if db.admin_status(user["_id"],current_chat_room):
            member_name_list.append("Delete event")
        else:
            member_name_list.append("Leave")
        self.ids.members.values = member_name_list
    def on_enter(self):
        self.start_message_update()
        self.get_all_members()
        current_event=self.event_details_setter(current_chat_room)
        self.ids.event_text.text=str(current_event["event_name"])+" "+str(current_event["event_location"])+" "+str(current_event["event_date"])+" "+str(current_event["event_time"])
    def start_message_update(self):
        Clock.schedule_interval(self.print_messages_periodically, 2)
    def event_details_setter(self,event_id):
        return db.get_event_info(current_chat_room)
    def print_messages_periodically(self,dt):
        messages = db.get_messages(current_chat_room)
        
        for message in messages:
            message_key = (message['userid'], message['message'], message['timestamp'])
            if message_key not in self.printed_messages:
                self.print_message(message['message'], message['timestamp'], message['userid'])
                self.printed_messages.add(message_key)
                
    def print_message(self, message, timestamp, userid):
        self.ids.chat_list.add_widget(
            MDFillRoundFlatButton(
                text=timestamp.strftime("%A, %B %d, %Y %I:%M %p")+"\n" + "You: "+message if userid == user["_id"] else timestamp.strftime("%A, %B %d, %Y %I:%M %p")+"\n"+db.get_user_name(userid)+": "+message, 
                pos_hint={'right': 1.0, 'y': 1.0} if userid == user["_id"] else {'left': 1.0, 'y': 1.0},
                size_hint=(0.5, 1),
                md_bg_color= "black" if userid == user["_id"] else "orange",
                theme_text_color="Custom",
                text_color= "orange" if userid == user["_id"] else "black",
                ),
        )
        print(message)
    def get_key_from_value(self,d,value):
        for k,v in d.items():
            if v==value:
                return k
        return None        
    def manage_members(self,action):
        if action=="Leave":
            db.leave_event(current_chat_room,user["_id"]) 
            app=MDApp.get_running_app()
            app.root.current="main"
        elif action=="Delete event":
            db.delete_event(current_chat_room)
            self.show_alert_dialog("Event deleted!")
            app=MDApp.get_running_app()
            app.root.current="main"
        elif action=="See members":
            pass
        elif db.admin_status(user["_id"],current_chat_room):
            user_id=self.get_key_from_value(self.members,action)
            print(str(user_id)+" asta e user id" )
            self.kick_dialog(action,current_chat_room,user_id)
        self.get_all_members()     
    def send_message(self):
        global current_chat_room
        text = self.ids.chatbox.text
        if self.ids.chatbox.text=="":
            pass
        else:
            self.ids.chatbox.text = ""
            db.insert_message(user["_id"], current_chat_room, text)
        
    def on_leave(self, *args):
        self.printed_messages = set()
        self.ids.chat_list.clear_widgets()
        self.ids.members.text="See members"
        Clock.unschedule(self.print_messages_periodically)
class WelcomeScreen(MDScreen):
    pass
class EditUser(MainPage,Register):
    global user
    def on_enter(self):
        self.ids.fullname.text=user["fullname"]
        self.ids.email.text=user["email"]
        self.ids.my_image.source="user.png"
    def edit_user(self):
        if(db.check_password(user["_id"],self.ids.password.text)):
            fullname=self.ids.fullname.text
            email=self.ids.email.text
            image=self.ids.my_image.source
            db.update_user(user["_id"],fullname,email,image)
            self.logout()
        else:
            self.show_alert_dialog("Wrong password!")
class EditEvent(CreateChatRoom,MainPage):
    global current_chat_room
    def on_enter(self):
        event=db.get_event_info(current_chat_room)
        print(event)
        self.ids.event_name.text=event["event_name"]
        self.ids.location.text=event["event_location"]
        self.ids.date.text=event["event_date"]
        self.ids.time.text=event["event_time"]
        self.ids.theme_spinner.text=event["event_theme"]
        self.ids.event_nr.text=str(event["event_nr"])
        self.ids.event_name.focus=True
class MyScreenManager(MDScreenManager):
    pass
class ChatRiseApp(MDApp):
    def build(self):
        self.theme_cls.theme_style="Dark"
        self.theme_cls.primary_palette="Orange"
        return Builder.load_file("chatrise.kv")
    
db=ChatRiseDB()
demo_app = ChatRiseApp()
demo_app.run()