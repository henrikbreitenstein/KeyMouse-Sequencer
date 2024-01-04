from .imports import *
import numpy as np
import multiprocessing as mp
from contextlib import contextmanager
from threading import Thread
from kivy.clock import mainthread

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
                
def get_start_view(_screen, RCcontrol) -> GridLayout:
    
    button_row_RecordPlay  = GridLayout( cols = 2 )
    button_row_FrameCount  = GridLayout( cols = 3 )
    button_row_ReplaySpeed = GridLayout( cols = 3 )

    #region button_row
    button_row_RecordPlay.add_widget(Button(
        text='Record', 
        on_release = lambda *args: Thread(target=RCcontrol.record_and_save, args=(_play,)).start())
    )

    _play = rec_circle_button(
        text='Play', 
        on_release = lambda *args: Thread(target=RCcontrol.play_indef, daemon=True).start())
    _play.make_rec_circ()
    _play.bind(pos=_play.green_ready, size=_play.green_ready)
    button_row_RecordPlay.add_widget(_play)
    
    button_row_FrameCount.add_widget(Button(
        text=f'-{RCcontrol.get_attr("speed_interval")}', 
        on_release = RCcontrol.decrease_speed)
    )
    button_row_FrameCount.add_widget(Button(
        text=f'+{RCcontrol.get_attr("speed_interval")}', 
        on_release = RCcontrol.increase_speed)
    )
    button_row_FrameCount.add_widget(Button(
        text='Set Frame Count', 
        on_release = RCcontrol.define_speed)
    )
    button_row_ReplaySpeed.add_widget(Button(
        text=f'-{RCcontrol.get_attr("factor_interval")}',
        on_release = RCcontrol.increase_speed_factor)
    )
    button_row_ReplaySpeed.add_widget(Button(
        text=f'+{RCcontrol.get_attr("factor_interval")}', 
        on_release = RCcontrol.decrease_speed_factor)
    )
    button_row_ReplaySpeed.add_widget(Button(
        text='Set Replay Speed', 
        on_release= RCcontrol.set_factor)
    )
    #endregion
    p_switch = partial(switch, _screen)

    w1_button_list = [
        button_row_RecordPlay,
        Button(text='Save', on_press = RCcontrol.save_to_file),
        Button(text='Load', on_press = RCcontrol.load_from_file),
        Button(text='View', on_press=p_switch('view')),
        Button(text='Sequencer', on_press=p_switch('sequencer')),
        button_row_FrameCount,
        button_row_ReplaySpeed,
        Button(text='Settings', on_press=p_switch('settings'))
    ]
    buttons = GridLayout(rows = len(w1_button_list))
    for _button in w1_button_list:
        buttons.add_widget(_button)

    start_layout = GridLayout(cols=2)
    start_layout.add_widget(buttons)
    start_layout.add_widget(FileChooserListView(rootpath='./saves'))
    return start_layout