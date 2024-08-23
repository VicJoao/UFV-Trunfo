

class WarningPopup(Popup):
    def __init__(self, text, **kwargs):
        super(WarningPopup, self).__init__(**kwargs)
        self.title = 'Warning'
        self.size_hint = (None, None)
        self.size = (400, 200)
        self.auto_dismiss = False
        self.add_widget(Label(text=text))
        self.add_widget(Button(text='OK', on_press=self.dismiss))