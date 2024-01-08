from .imports import *

class settings_screen(Screen):

    def __init__(self, widgets):
        Screen.__init__(self)
        self.widgets = widgets

    def on_pre_enter(self):
        app = App.get_running_app()
        settings_dict = app.settings_dict
        for category, settings in settings_dict.items():
            for setting, value in settings.items():
                self.widgets[setting].text = str(value)
        return True

class TreeViewText(GridLayout, TreeViewNode):
    pass

def on_focus(settings_dict, category, setting, instance, value):
    if not value:
        try:
            F_cast = float(instance.text)
            I_cast = int(instance.text)
            if F_cast == I_cast:
                settings_dict[category][setting] = I_cast
            else:
                settings_dict[category][setting] = F_cast
        except:
            settings_dict[category][setting] = instance.text

def create_and_append_TextInput(category, setting, settings_dict, widgets):
    _widget = TextInput(text=str(settings_dict[category][setting]), multiline=False)
    _widget.bind(focus=partial(on_focus, settings_dict, category, setting))
    widgets[setting] = _widget
    return _widget

def get_settings_view(settings_dict, update_settings, screens) -> TreeView:
    
    settings_layout = GridLayout(rows=2)
    
    widgets = {}
    _screen = settings_screen(widgets)
    _screen.name = 'settings'

    # ------ Taskbar -----
    p_switch = partial(switch, _screen) 


    def wrap(*args):
        update_settings(settings_dict)
        switch(_screen, 'start')()
    
    menu_buttons = [
        Button(text = 'Back', on_press=wrap),
    ]
    
    taskbar = GridLayout(cols=len(menu_buttons), size_hint_y = None, height=40)
    for _button in menu_buttons:
        taskbar.add_widget(_button)
    
    # ------- Tree -------
    p_TextInput = partial(
        create_and_append_TextInput,
        settings_dict = settings_dict,
        widgets = widgets
    )
    _scroll_view = ScrollView(do_scroll_x = False)
    settings_tree = TreeView(hide_root=True, size_hint_y=None)
    settings_tree.bind(minimum_height = settings_tree.setter('height'))
    for category in settings_dict.keys():
        level_1 = settings_tree.add_node(TreeViewLabel(text=category))
        for setting in settings_dict[category].keys():
            node = TreeViewText(cols=2, height=30)
            node.add_widget(TreeViewLabel(text=setting))
            _textinput = p_TextInput(category, setting)
            node.add_widget(_textinput)
            settings_tree.add_node(node, level_1)
    _scroll_view.add_widget(settings_tree)

    settings_layout.add_widget(taskbar)
    settings_layout.add_widget(_scroll_view)
    _screen.add_widget(settings_layout)
    screens.append(_screen)