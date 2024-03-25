from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget


class Example(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return (
            MDScrollView(
                MDList(
                    OneLineAvatarIconListItem(
                        IconLeftWidget(
                            icon="github"
                        ),
                        on_release=lambda x: print("Click!")
                    ),
                    OneLineAvatarIconListItem(
                        IconLeftWidget(
                            icon="gitlab"
                        ),
                        on_release=lambda x: print("Click 2!")
                    ),
                )
            )
        )


Example().run()