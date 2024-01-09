from .imports import *
from threading import Thread

def colored_background(instance, value):
    if (instance.pos[0] < 100) & (instance.pos[1] < 100):
        return None
    
    instance.canvas.before.clear()    
    with instance.canvas.before:
        Color(0.5,0.5,0.5,0.5)
        Rectangle(pos=instance.pos, size=instance.size)



class update_buttons_screen(Screen):

    def __init__(self):
        Screen.__init__(self)
        self.watch = {}
        self.widgets = {}

    def set_widgets(self, watch, widgets):
        self.watch = watch
        self.widgets = widgets
    def on_pre_enter(self):
        app = App.get_running_app()
        settings_dict = app.settings_dict
        RCcontrol = app.RCcontrol

        self.widgets['LoadSettings'].text = (
            "[b]Load Fpi/Speed[/b]\n" 
            + f"Fpi: {RCcontrol.load_speed:.2g}  |  Speed: {RCcontrol.load_speed_factor:.2g}\n"
            + f"Name: {RCcontrol.filename}")

        font_size = int(settings_dict['interface']['Font size'])
        for key, instance in self.watch['controller'].items():
            instance.text = f"{key[0]}" + f"{settings_dict['controller'][key[1]]:.2g}"
            instance.font_size = font_size*Metrics.dp
        for key, instance in self.watch['hotkeys'].items():
            hk = settings_dict['hotkeys'][key[1]]
            instance.font_size = font_size*Metrics.dp
            if hk != '':
                instance.text = key[0] + '\n' + hk
        
class rec_circle_button(Button):

    def make_rec_circ(self):
        self.radius = 10
        with self.canvas.after:
            Color(0, 1, 0, 1)
            self.rec_circle = Ellipse(
                pos = (0, 0),
                size = (0, 0)
            )
        self.anim_call_flag = 0

    def green_ready(self, *args):
        self.rec_circle.pos = (
            self.center_x - self.width*2/7 - self.radius, 
            self.center_y - self.radius)
        self.rec_circle.size = (2*self.radius, 2*self.radius)

    def create_red_circle(self):
        with self.canvas.after:
            Color(1, 0, 0, 1)
            red_circ = Ellipse(
                pos = (
                self.center_x - self.width*2/7 - self.radius, 
                self.center_y - self.radius),
                size = (2*self.radius, 2*self.radius))

    def recording_blink(self):
        if self.anim_call_flag == 0:
            Clock.schedule_once(lambda *args: self.canvas.after.clear())
            self.create = Clock.schedule_interval(lambda *args: self.create_red_circle(), 1)
            self.destroy = Clock.schedule_interval(lambda *args: self.canvas.after.clear(), 2)
            self.anim_call_flag = 1
        else:
            self.create.cancel()
            self.destroy.cancel()
            Clock.schedule_once(lambda *args: self.canvas.after.clear())
            Clock.schedule_once(lambda *args: self.make_rec_circ())
            Clock.schedule_once(lambda *args: self.green_ready())
            self.anim_call_flag = 0

def create_button_append_watch(category, key_0, key_1, func, settings_dict, watch_dict, widget_dict):
    _button = Button(text=f'{key_0}{settings_dict[category][key_1]}', markup=True, halign='center',
                     on_release=func)
    watch_dict[category][(key_0, key_1)] = _button
    widget_dict[key_1] = _button
    return _button

def get_start_view(RCcontrol, settings_dict, screens) -> GridLayout:

    _screen = update_buttons_screen()
    _screen.name ='start'
    watch = {}
    widgets = {}
    for key in settings_dict.keys():
        watch[key] = {}
    p_create_append = partial(
        create_button_append_watch, 
        settings_dict=settings_dict, 
        watch_dict=watch, 
        widget_dict=widgets)

    button_row_RecordPlay  = GridLayout( cols = 2 )
    button_row_FrameCount  = GridLayout( cols = 3 )
    button_row_ReplaySpeed = GridLayout( cols = 3 )

    #region button_row
    record_func = lambda *args: Thread(target=RCcontrol.record_and_save).start()
    record_button = p_create_append('hotkeys', '[b]Record[/b]', 'Record', record_func)
    button_row_RecordPlay.add_widget(record_button)
    play_func = lambda *args: Thread(target=RCcontrol.play_indef, daemon=True).start()
    _play = rec_circle_button(text='[b]Play[/b]', markup=True, halign='center', on_release=play_func)
    _play.make_rec_circ()
    _play.bind(pos=_play.green_ready, size=_play.green_ready)
    watch['hotkeys'][('[b]Play[/b]', 'Play')] = _play
    button_row_RecordPlay.add_widget(_play)
    
    speed_dec_button  = p_create_append('controller', '-', 'Speed_interval', RCcontrol.decrease_speed)
    speed_inc_button  = p_create_append('controller', '+', 'Speed_interval', RCcontrol.increase_speed)
    factor_dec_button = p_create_append('controller', '-', 'Factor_interval', RCcontrol.decrease_speed_factor)
    factor_inc_button = p_create_append('controller', '+', 'Factor_interval', RCcontrol.increase_speed_factor)
    define_speed_btn  = p_create_append('controller', '[b]Fpi[/b]\n', 'Speed', lambda *args: None)
    define_factor_btn = p_create_append('controller', '[b]Speed[/b]\n', 'Factor', lambda *args: None)
    button_row_FrameCount.add_widget(speed_dec_button)
    button_row_FrameCount.add_widget(speed_inc_button)
    button_row_FrameCount.add_widget(define_speed_btn)
    button_row_ReplaySpeed.add_widget(factor_dec_button)
    button_row_ReplaySpeed.add_widget(factor_inc_button)
    button_row_ReplaySpeed.add_widget(define_factor_btn)
    #endregion
    p_switch = partial(switch, _screen)

    LoadSettings_btn = Button(text='[b]Load Fpi/Speed[/b]', markup=True, halign='center',
                             on_release=lambda *args: RCcontrol.load_settings())   
    watch['LoadSettings'] = LoadSettings_btn
    widgets['LoadSettings'] = LoadSettings_btn

    def on_active(text, checkbox, value):
        match text:
            case 'Mouse':
                if value:
                    RCcontrol.record_mouse = True
                else:
                    RCcontrol.record_mouse = False
            case 'Keys':
                if value:
                    RCcontrol.record_keys = True
                else:
                    RCcontrol.record_keys = False
    
    checkbox_row = GridLayout(cols=2)
    mouse_col = GridLayout(rows=2)
    mouse_col.bind(size=colored_background)
    keys_col = GridLayout(rows=2)
    keys_col.bind(size=colored_background)
    mouse_label = Label(text='Mouse')
    keys_label = Label(text='Keys')
    checkbox_mouse = CheckBox()
    checkbox_mouse._set_active('down')
    checkbox_keys = CheckBox()
    checkbox_keys._set_active('down')
    checkbox_mouse.bind(active=lambda *args: on_active('Mouse', *args))
    checkbox_keys.bind(active=lambda *args: on_active('Keys', *args))

    mouse_col.add_widget(mouse_label)
    mouse_col.add_widget(checkbox_mouse)
    keys_col.add_widget(keys_label)
    keys_col.add_widget(checkbox_keys)

    checkbox_row.add_widget(mouse_col)
    checkbox_row.add_widget(keys_col)

    w1_button_list = [
        button_row_RecordPlay,
        checkbox_row,
        p_create_append('hotkeys', '[b]Save[/b]', 'Save', lambda *args: RCcontrol.save_to_file()),
        LoadSettings_btn,
        p_create_append('hotkeys', '[b]View[/b]', 'View', p_switch('view')),
        p_create_append('hotkeys', '[b]Sequencer[/b]', 'Sequencer', p_switch('sequencer')),
        button_row_FrameCount,
        button_row_ReplaySpeed,
        p_create_append('hotkeys', '[b]Settings[/b]', 'Settings', p_switch('settings'))
    ]
    buttons = GridLayout(rows = len(w1_button_list))
    for _button in w1_button_list:
        buttons.add_widget(_button)

    start_layout = GridLayout(cols=2)
    start_layout.add_widget(buttons)


    FileSelect = FileChooserListView(rootpath=settings_dict['interface']['Files Path'], dirselect=False)
    FileSelect.bind(on_submit=RCcontrol.load_from_file)
    widgets['FileChooser'] = FileSelect
    start_layout.add_widget(FileSelect)
   
    _screen.add_widget(start_layout)
    _screen.set_widgets(watch, widgets)
    screens.append(_screen)