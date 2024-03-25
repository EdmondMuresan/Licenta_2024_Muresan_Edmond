from mydb import ChatRiseDB
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.list import MDList
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from datetime import datetime
from kivymd.uix.pickers import MDDatePicker,MDTimePicker
from PIL import Image
import io
user={}
current_chat_room=None
class AllertDialog():
    dialog=None
    def show_alert_dialog(self,info):
        self.dialog = MDDialog(
            title="Caution!",
            text=info,
            buttons=[
                MDRoundFlatButton(
                    text="Ok",
                    text_color=(240, 20, 20, 1),
                    on_release = self.close_dialog
                    ),
                ]
            )
        self.dialog.open()
    
    def close_dialog(self,obj):
        self.dialog.dismiss()
class EventDetails(AllertDialog):
    def show_info_dialog(self,title,info,event_id,user_id,use_case):
        if use_case=="join":
            self.dialog = MDDialog(
                title=title,
                text=info,
                buttons=[
                    MDRoundFlatButton(
                        text="Join",
                        text_color=(240, 20, 20, 1),
                        on_release=lambda x, event_id=event_id, user_id=user_id: self.connect_to_event(event_id, user_id)
                    ),
                    MDRoundFlatButton(
                        text="Cancel",
                        text_color=(240, 20, 20, 1),
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
                        text_color=(240, 20, 20, 1),
                        on_release=lambda x, event_id=event_id, user_id=user_id: self.change_room(event_id))
                ,
                MDRoundFlatButton(
                        text="Cancel",
                        text_color=(240, 20, 20, 1),
                        on_release = self.close_dialog
                        )
                ]
            )
        self.dialog.open()
    def change_room(self,event_id):
        global current_chat_room
        current_chat_room=event_id
        app=MDApp.get_running_app()
        app.root.current="chatroom"
    def connect_to_event(self,event_id,user_id):
        if(db.connect_to_event(event_id,user_id,"join")):
            self.show_alert_dialog("Success")
        else:
            self.show_alert_dialog("Error")
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
                print(filename[0])
            else:
                self.show_alert_dialog("Invalid image format!")
        except:
            pass
class Login(MDScreen,AllertDialog):
    dialog=None
    def login(self):
        global user
        email=self.ids.email.text
        password=self.ids.password.text
        self.ids.email.text=""
        self.ids.password.text=""
        if(db.login_user(email,password)):
            app=MDApp.get_running_app()
            app.root.current="main"
            user=db.getinfo(email)
            print(str(user)+"Welcome")
            
        else:
            self.show_alert_dialog("Invalid credentials!")
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
    def create_event(self):
        global user
        user_id=user['_id']
        event_name=self.ids.event_name.text
        event_nr=self.ids.event_nr.text
        event_location=self.ids.location.text
        event_theme=self.ids.theme_spinner.text
        event_date=self.ids.date.text
        event_time=self.ids.time.text
        if event_name =="" or event_nr=="" or event_location=="" or event_theme=="Select Theme":
            self.show_alert_dialog("Invalid data!")
        else:
            db.insert_event(user_id,event_name,event_nr,event_location,event_theme,event_date,event_time)
            app=MDApp.get_running_app()
            app.root.current="main"
            self.show_alert_dialog("Event created!")
class MainPage(MDScreen,EventDetails):
    def logout(self):
        global user
        user={}
        app=MDApp.get_running_app()
        app.root.current="login"
        print(user)
    def on_enter(self):
        global user
        self.ids.user_button.text="Welcome"+" "+str(user["fullname"])
        image = Image.open(io.BytesIO(user['image']))
        image.save('user.png')
        self.ids.user_image.source="user.png"
        self.load_events(True,"join")	
    def load_events(self,type,use_case):
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
            if db.connect_to_event(event_id,user["_id"],"view")==type:
                item = OneLineAvatarIconListItem(
                    IconLeftWidget(icon="human-capacity-increase"),
                    on_release=lambda x, eventid=event_id,loc=event_location, theme=event_theme, date=event_date, time=event_time, nr=event_nr, name=event_name: self.show_info_dialog(f"{name} ~~ Event details", f" Location:{loc} \n Theme:{theme} \n Date:{date} Time:{time} \n Available slots: {nr-len(event['participants'])}",event_id,user["_id"],use_case),
                    text=f"{event['event_name']} {event['event_date']}"
                )
                list_view.add_widget(item)
        self.ids.event_box.add_widget(list_view)
    def change_mine(self):
        self.ids.event_box.clear_widgets()
        self.load_events(False,"message")
    def change_not_mine(self):
        self.ids.event_box.clear_widgets()
        self.load_events(True,"join")	
    def on_leave(self, *args):
        self.ids.event_box.clear_widgets()
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