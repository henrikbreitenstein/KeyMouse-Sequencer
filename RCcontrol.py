import mouse as ms
import keyboard as kb
import pickle as pk
import numpy as np
import time
import sys
from threading import Thread
from typing import Callable
from kivy.logger import Logger
from functools import partial
from contextlib import contextmanager
from kivy.clock import mainthread

class recorder():
    def __init__(self, settings: dict):
        self.speed = settings['Speed']
        self.speed_factor = settings['Factor'] 
        self.speed_interval = settings['Speed_interval']
        self.factor_interval = settings['Factor_interval']
        self.rec = []
        

    def get_attr(self, attr_str):
        attr = eval(f'self.{attr_str}')
        return attr

    def record_and_save(self, _play):

        Logger.info('Controller: Recording')
        _play.recording_blink()
        self.rec = ms.record()
        _play.recording_blink()
        Logger.info('Controller: Stopped recording')

    def play_indef(self, button_instance=None):
        play_rec = []
        i = 0
        for event in self.rec:
            if type(event) == ms._mouse_event.ButtonEvent:
                play_rec.append(event)
            elif i >= self.speed:
                play_rec.append(event)
                i = 0
            i += 1
        
        splits = [[play_rec[i] for i in range(a, a+5)] for a in np.arange(0, len(play_rec)-5, 5)]
        while not kb.is_pressed('alt'): 
            for k in range(len(splits)- 1):
                if kb.is_pressed('alt'):
                    break
                ms.play(splits[k], speed_factor=self.speed_factor)
                time.sleep((splits[k+1][0][2] - splits[k][-1][2])/self.speed_factor)

    def combine(self, button_instance=None):
        name = 0
        files = []
        while name != '':
            name = input('Add file to timeline:') 
            files.append(name)

        del files[-1]

        mults = []
        for name in files:
            mults.append(eval(input(f'Multiples of {name}:')))
        
        for file, mult in zip(files, mults):
            with open(file, 'rb') as f:
                [self.speed, self.speed_factor, self.rec] = pk.load(f)
            
            play_rec = []
            i = 0
            for event in self.rec:
                if type(event) == ms._mouse_event.ButtonEvent:
                    play_rec.append(event)
                elif i >= self.speed:
                    play_rec.append(event)
                    i = 0
                i += 1
            
            splits = [[play_rec[i] for i in range(a, a+5)] for a in np.arange(0, len(play_rec)-5, 5)]
            for _ in range(mult):
                for k in range(len(splits)- 1):
                    if kb.is_pressed('alt'):
                        break
                    ms.play(splits[k], speed_factor=self.speed_factor)
                    time.sleep((splits[k+1][0][2] - splits[k][-1][2])/self.speed_factor)

    def increase_speed(self, button_instance=None):
        self.speed += 1
        print(f'Speed of recording set to {self.speed}')

    def decrease_speed(self, button_instance=None):
        self.speed -= 1
        print(f'Speed of recording set to {self.speed}')

    def define_speed(self):
        val = int(input('set speed to:'))
        self.speed = val
    
    def increase_speed_factor(self, button_instance=None):
        self.speed_factor += self.factor_interval

    def decrease_speed_factor(self, button_instance=None):
        self.speed_factor -= self.factor_interval

    def save_to_file(self, button_instance=None):
        if self.rec == []:
            print('Empty Recording')
            return None
        file_name = input('Save, Enter file name:')
        if file_name == '':
            return None
        with open(file_name, 'wb') as f:
            pk.dump([self.speed, self.speed_factor, self.rec], f)

    def load_from_file(self, button_instance=None):
        file_name = input('Load, Enter file name:')
        if file_name == '':
            return None
        with open(file_name, 'rb') as f:
            [self.speed, self.speed_factor, self.rec] = pk.load(f)

    def list_clicks(self, button_instance=None, verbose=True):
        i = 0
        clicks = []
        print("\n")
        last_move = ms._mouse_event.MoveEvent(0, 0, 0)
        for event in self.rec[:-1]:
            if type(event)==ms._mouse_event.MoveEvent:
                last_move = event
            if type(event)==ms._mouse_event.ButtonEvent:
                clicks.append(i)
                if verbose:
                    print("-"*80)
                    print(f"Click {len(clicks)-1}, Time: {event[2]}, Last move coordinates: ({last_move[0]}, {last_move[1]})")
            i += 1
        print("\n")
        self.clicks = np.array(clicks)

    def remove_click(self, button_instance=None):
        self.list_clicks(verbose=False)
        numbers= eval(input('indexes to delete, list ([index1, index2, ...]):'))
        for n in numbers:
            del self.rec[self.clicks[n]]
        
    def set_speed(self, button_instance=None):
        play_rec = []
        i = 0
        for event in self.rec:
            if type(event) == ms._mouse_event.ButtonEvent:
                play_rec.append(event)
            elif i >= self.speed:
                play_rec.append(event)
                i = 0
            i += 1
        self.rec = play_rec
        self.speed=1

    def set_factor(self, button_instance=None):
        factor = eval(input('Set factor for mouse.play:'))
        if factor == '':
            return None
        self.speed_factor = factor

