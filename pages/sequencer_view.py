from .imports import *
from kivy.uix.screenmanager import NoTransition
import numpy as np

class file_seq_layout(GridLayout):

    def __init__(self, _manager):
        GridLayout.__init__(self, rows=4)

        self.delete_btn  = Button(
            text = 'Remove',
            on_release=lambda *args: self.remove(_manager))
        
        self.file = ''
        self.repeats = GridLayout(rows=2, size_hint_y=None)
        self.repeats.add_widget(Label(text='Repeats', limit_render_to_text_bbox=True))
        self.nrepeats = TextInput(text='1', multiline=False)
        self.repeats.add_widget(self.nrepeats)

        self.move = GridLayout(cols=2)
        self.title = Label(size_hint_y=None, limit_render_to_text_bbox=True)
        
        self.add_widget(self.title)
        self.add_widget(self.repeats)
        self.add_widget(self.move)
        self.add_widget(self.delete_btn)

    def remove(self, _manager):
        self.file = ''
        _manager.current = 'before'

class load_screen(Screen):

    def __init__(self, Chooser):
        Screen.__init__(self)
        self.Chooser = Chooser


    def on_pre_enter(self):
        self.Chooser._update_files()
        return True

def on_submit(MainManager, loaders_list, layouts, *args):

    if not args[1]:
        return None

    filename = args[1][0]
    MainManager.current = 'main'
    loaders_list[global_i].current = 'after'
    for i in np.arange(len(filename)-1, -1, -1):
        if filename[i] == '\\':
            text_pre = filename[i+1:]
            text_post = ''
            for char in text_pre:
                if (char == ' ') or (char == '_'):
                    text_post += '\n'
                else:
                    text_post += char
            layouts[global_i].title.text = text_post
            layouts[global_i].file = filename
            break

def load_file(MainManager, load_buttons, instance):
    global global_i
    MainManager.current = 'load'
    for i, btn in enumerate(load_buttons):
        if instance == btn:
            break
    global_i = i

def load_button(loaders_list, layouts, load_buttons, MainManager):
    
    _manager = ScreenManager(transition=NoTransition())
    before_load = Screen(name='before')
    after_load = Screen(name='after')
    _manager.add_widget(before_load)
    _manager.add_widget(after_load)

    layout = file_seq_layout(_manager)
    layouts.append(layout)

    #region before
    _button = Button(on_release=partial(load_file, MainManager, load_buttons))
    _button.background_color = (150/255, 150/255, 150/255, 0.4)
    _button.text = '[b]+[/b]'
    _button.markup = True
    _button.outline_color = (0, 0, 0, 1)
    _button.outline_width = 2
    _button.bind(on_release=switch(before_load, 'after'))
    before_load.add_widget(_button)
    load_buttons.append(_button)
    #endregion

    after_load.add_widget(layout)
    loaders_list.append(_manager)

    return _manager

def get_sequence(layouts, RCcontrol, _screen):

    files = []
    mults = []
    for layout in layouts:
        if layout.file != '':
            files.append(layout.file)
            mults.append(int(layout.nrepeats.text))

    _screen.manager.current = 'start'
    RCcontrol.combine(files, mults)

def get_sequencer_view(screens, RCcontrol, filepath):

    _screen = Screen()
    _screen.name = 'sequencer'

    Back = Button(text='Back', on_release=switch(_screen, 'start'))
    Save = Button(
        text ='Save',
        on_release = lambda *args: get_sequence(layouts, RCcontrol, _screen))

    menu = [
        Back,
        Save,
    ]

    taskbar = GridLayout(cols=len(menu), size_hint_y = None, height=40)
    for _widget in menu:
        taskbar.add_widget(_widget)
    
    layout = GridLayout(rows=2)
    layout.add_widget(taskbar)

    _manager = ScreenManager(transition=NoTransition())
    MainScreen = Screen(name='main')
    Chooser = FileChooserListView(rootpath=filepath, dirselect=False)
    LoadScreen = load_screen(Chooser)
    LoadScreen.name = 'load'
    LoadScreen.add_widget(Chooser)
    N_loaders = 10
    MainGrid = GridLayout(cols=N_loaders)
    loaders_list = []
    layouts = []
    load_buttons = []
    Chooser.bind(on_submit=partial(on_submit, _manager, loaders_list, layouts))

    for _ in range(N_loaders):
        loader = load_button(loaders_list, layouts, load_buttons, _manager)
        MainGrid.add_widget(loader)

    MainScreen.add_widget(MainGrid)
    _manager.add_widget(MainScreen)
    _manager.add_widget(LoadScreen)
    layout.add_widget(_manager)
    _screen.add_widget(layout)
    screens.append(_screen)