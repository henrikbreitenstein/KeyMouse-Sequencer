import mouse as ms
import keyboard as kb
import pickle as pk
import time
import sys
from numpy import arange, array, argsort
from collections import namedtuple
from kivy.logger import Logger
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
import platform as _platform
if _platform.system() == 'Windows':
    from mouse import _winmouse as _os_mouse
elif _platform.system() == 'Linux':
    from mouse import _nixmouse as _os_mouse

class recorder():
    def __init__(self, settings: dict, start):
        
        self.rec_flag = 0
        self.playing_flag = 0
        self.record_mouse = True
        self.record_keys = True
        self.stop_play = 'alt'
        self._play = None
        self.start = start
        self.filename = "Empty Recording"

        self.stop = settings['Stop']
        self.speed = settings['Speed']
        self.speed_interval = settings['Speed_interval']
        self.load_speed = self.speed
        
        self.speed_factor = settings['Factor'] 
        self.factor_interval = settings['Factor_interval']
        self.load_speed_factor = self.speed_factor
        
        self.update_buttons = lambda *args: None #defined in main
        self.filechooser= None
        self.settings = settings
        self.rec = []
        self.k_rec = []

    def update_values(self, settings, start):
        self.start = start
        self.stop_play = settings['Stop_Play']
        self.stop = settings['Stop']
        self.speed = settings['Speed']
        self.speed_factor = settings['Factor'] 
        self.speed_interval = settings['Speed_interval']
        self.factor_interval = settings['Factor_interval']

    def record_and_save(self):
        if not self.rec_flag:   
            self.k_rec = []
            self.rec = []
            self._play.recording_blink()
            if self.record_mouse:
                ms.hook(self.rec.append)
            if self.record_keys:
                kb.hook(self.k_rec.append)
            
            self.rec_flag = 1
            kb.wait(self.stop)
            if len(self.k_rec) > 0:
                for i in [2, 1]:
                    if len(self.k_rec) >= i:
                        if self.k_rec[-1].name in self.stop:
                            del self.k_rec[-i]
                    if len(self.k_rec) >= i:
                        if self.k_rec[i].name in self.start:
                            del self.k_rec[i]

            if self.record_mouse:
                ms.unhook(self.rec.append)
            if self.record_keys:
                kb.unhook(self.k_rec.append)

            self._play.recording_blink()        
            self.rec_flag = 0
        else:
            Logger.info(f'RCcontrol: Press {self.stop} to stop recording')

    def get_play_rec(self, rec, k_rec):
        play_rec = []
        prev_m = self.record_mouse
        prev_k = self.record_keys

        if (len(rec) + len(k_rec)) < 10:
            return play_rec
        
        if len(rec) < 1:
            self.record_mouse = False
        if len(k_rec) < 1:
            self.record_keys = False


        if self.record_mouse and (not self.record_keys):
            i = 0
            for event in rec:    
                if type(event) == ms._mouse_event.ButtonEvent:
                    play_rec.append(event)
                elif i >= self.speed:
                    play_rec.append(event)
                    i = 0
                i += 1

            return play_rec

        elif (not self.record_mouse) and self.record_keys:

            return k_rec

        elif self.record_mouse and self.record_keys:
            
            i = 0
            fpi_rec = []
            for event in rec:
                if type(event) == ms._mouse_event.ButtonEvent:
                    fpi_rec.append(event)
                elif i >= self.speed:
                    fpi_rec.append(event)
                    i = 0
                i += 1

            full_rec = array(fpi_rec + k_rec)
            time_line = array([event.time for event in full_rec])
            sorted = full_rec[argsort(time_line)]
            play_rec = list(sorted)
                
        self.record_mouse = prev_m
        self.record_keys = prev_k
        return play_rec
    
    def play_indef(self, *args):
        if not self.playing_flag:
            pressed_downs = []
            self.playing_flag = 1
            play_rec = self.get_play_rec(self.rec, self.k_rec)
            if len(play_rec) > 0:
                last_time = play_rec[0].time
            else:
                self.playing_flag = 0
                Logger.info('RCcontrol: Recording Empty')
                return None

            for event in play_rec:
                if kb.is_pressed(self.stop_play):
                    break
                wait = event.time - last_time
                if wait > 0:
                    time.sleep(wait/self.speed_factor)
                last_time = event.time

                match type(event):
                    case ms._mouse_event.MoveEvent:
                        _os_mouse.move_to(event.x, event.y)
                    case ms._mouse_event.ButtonEvent:
                        if event.event_type == ms._mouse_event.UP:
                            _os_mouse.release(event.button)
                        else:
                            _os_mouse.press(event.button)
                    case ms._mouse_event.WheelEvent:
                        _os_mouse.wheel(event.delta)
                    case kb._keyboard_event.KeyboardEvent:
                        if event.event_type == kb._keyboard_event.KEY_DOWN:
                            pressed_downs.append(event.scan_code or event.name)
                            kb.press(event.scan_code or event.name)
                        else:
                            kb.release(event.scan_code or event.name)
                    case _:
                        Logger.info('Controller: Nop')


            while not kb.is_pressed(self.stop_play):
                for event in play_rec:
                    if kb.is_pressed(self.stop_play):
                        break
                    wait = event.time - last_time
                    if wait > 0:
                        time.sleep(wait/self.speed_factor)
                    last_time = event.time

                    match type(event):
                        case ms._mouse_event.MoveEvent:
                            _os_mouse.move_to(event.x, event.y)
                        case ms._mouse_event.ButtonEvent:
                            if event.event_type == ms._mouse_event.UP:
                                _os_mouse.release(event.button)
                            else:
                                _os_mouse.press(event.button)
                        case ms._mouse_event.WheelEvent:
                            _os_mouse.wheel(event.delta)
                        case kb._keyboard_event.KeyboardEvent:
                            if event.event_type == kb._keyboard_event.KEY_DOWN:
                                kb.press(event.scan_code or event.name)
                            else:
                                kb.release(event.scan_code or event.name)
                        case _:
                            Logger.info('Controller: Nop')
                        
                for key in pressed_downs:
                    kb.release(key)

            for key in pressed_downs:
                kb.release(key)
            self.playing_flag = 0
            ms.release('left')
            ms.release('right')
        else:
            Logger.info('Controller: Allready playing')

    def combine(self, files, mults):
        rec_c = []
        k_rec_c = []
        prev_rec = self.record_keys
        self.record_keys = False
        if len(files) < 1 or len(files) != len(mults):
            return None
        
        last_time = 0
        for file, mult in zip(files, mults):
            if mult <= 0 :
                continue
            with open(file, 'rb') as f:
                rec_temp = []

                [self.speed, self.speed_factor, self.rec, self.k_rec] = pk.load(f)
                
                #To ensure the starttime of next macro is lower than the end of the previous
                if (len(self.rec) > 0) and (len(self.k_rec) > 0):
                    if self.rec[0].time < self.k_rec[0].time:
                        last_time = self.rec[0].time
                    else:
                        last_time = self.k_rec[0].time
                elif (len(self.rec) > 0):
                    last_time = self.rec[0].time
                elif (len(self.k_rec) > 0):
                    last_time = self.k_rec[0].time
                else:
                    continue

                for event in self.k_rec:
                    event.time = (event.time - last_time)/self.speed_factor

                self.rec = self.get_play_rec()
                for event in self.rec:
                    rec_temp.append(type(event)(event[0], event[1], (event.time - last_time)/self.speed_factor))
                
                rec_c += rec_temp
                k_rec_c += self.k_rec

        self.speed = 1
        self.speed_factor = 1
        self.record_keys = prev_rec
        self.rec = rec_c
        self.k_rec = k_rec_c
        self.settings['Speed'] = 1
        self.settings['Factor'] = 1
        self.save_to_file()

    def increase_speed(self, *args):
        self.speed += self.speed_interval
        self.settings['Speed'] = self.speed
        self.update_buttons()

    def decrease_speed(self, *args):
        self.speed -= self.speed_interval
        self.settings['Speed'] = self.speed
        self.update_buttons()

    def increase_speed_factor(self, *args):
        self.speed_factor += self.factor_interval
        self.settings['Factor'] = self.speed_factor
        self.update_buttons()

    def decrease_speed_factor(self, *args):
        self.speed_factor -= self.factor_interval
        self.settings['Factor'] = self.speed_factor
        self.update_buttons()

    def save_to_file(self):
        FileChooser = self.filechooser
        layout = GridLayout(rows=2, size_hint_y=None)
        def save_file(instance):
            value = instance.text
            if value != '':    
                current_dir = FileChooser.path
                with open(current_dir+ f'/{value}', 'wb') as fp:
                    pk.dump([self.speed, self.speed_factor, self.rec, self.k_rec], fp)
            FileChooser.remove_widget(layout)
            FileChooser._update_files()

        InstructionLabel = Label(text='Insert file name', size_hint_y=None, height=30)
        FileNameInput = TextInput(
            size_hint_y=None,
            multiline = False, 
            height=30)
        FileNameInput.bind(on_text_validate=save_file)
        layout.add_widget(InstructionLabel)
        layout.add_widget(FileNameInput)
        FileChooser.add_widget(layout, index=-1)
        FileNameInput.focus = True

    def load_from_file(self, *args):
        
        if not args[1]:
            return None
        
        file = args[1][0]
        for i in arange(len(file)-1, -1, -1):
            if file[i] == '\\':
                text_pre = file[i+1:]
                break
        self.filename = text_pre

        with open(file, 'rb') as f:
            [self.load_speed, self.load_speed_factor, self.rec, self.k_rec] = pk.load(f)
            self.update_buttons()
    
    def load_settings(self, *args):
        self.speed = self.load_speed
        self.settings['Speed'] = self.speed
        self.speed_factor = self.load_speed_factor
        self.settings['Factor'] = self.speed_factor
        self.update_buttons()