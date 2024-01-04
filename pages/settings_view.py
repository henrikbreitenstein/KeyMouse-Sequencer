from .imports import *

def get_settings_view(_screen, RCcontrol, settings_dict) -> TreeView:
    settings_layout = GridLayout(rows=2)
    
    # ------ Taskbar ------
    p_switch = partial(switch, _screen)
    menu_buttons = [
        Button(text = 'Back', on_press=p_switch('start')),
    ]

    taskbar = GridLayout(cols=len(menu_buttons), size_hint_y = None, height=40)
    for _button in menu_buttons:
        taskbar.add_widget(_button)
    
    # ------- Tree -------
    _scroll_view = ScrollView(do_scroll_x = False)
    settings_tree = TreeView(hide_root=True, size_hint_y=None)
    settings_tree.bind(minimum_height = settings_tree.setter('height'))
    for category in settings_dict.keys():
        level_1 = settings_tree.add_node(TreeViewLabel(text=category))
        for setting in settings_dict[category].keys():
            settings_tree.add_node(TreeViewLabel(text=setting), level_1)
    _scroll_view.add_widget(settings_tree)

    settings_layout.add_widget(taskbar)
    settings_layout.add_widget(_scroll_view)
    return settings_layout