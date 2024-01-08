
import json
import time
import os
import sys
import keyboard as kb
import mouse as ms
import win32timezone
#os.chdir(sys._MEIPASS) #for freezing with pyinstaller

from typing import Callable
from functools import partial
from multiprocessing.managers import SyncManager
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.app import App
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.graphics import *
from pages.utils import switch
from threading import Thread
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager, NoTransition
from RCcontrol import recorder
from pages.start_view import get_start_view
from pages.settings_view import get_settings_view
from pages.view_view import get_view_view
from pages.sequencer_view import get_sequencer_view

class KeyMouse_Sequencer(App):

    def __init__(self):
        App.__init__(self)
        with open('settings.json') as fjson:
            self.settings_dict = json.load(fjson)
        if not os.path.isdir(self.settings_dict['interface']['Files Path']):
            self.settings_dict['interface']['Files Path'] = './saves'
            if not os.path.isdir('./saves'):
                os.mkdir('./saves')

    def on_stop(self, *args):
        with open('settings.json', 'w') as fjson:
            json.dump(self.settings_dict, fjson, ensure_ascii=False)
        return True
    
    def build_config(self, config):
        config.setdefaults('mouse', {'disable_multitouch' : 'True'})

    def build(self):
        config = self.config
        self.RCcontrol = recorder(
            self.settings_dict['controller'], 
            self.settings_dict['hotkeys']['Record'])


        def update_settings(settings_dict):
            self.settings_dict = settings_dict
            self.RCcontrol.update_values(
                settings_dict['controller'],
                settings_dict['hotkeys']['Record'])
            kb.unhook_all_hotkeys()
            shortcuts = self.settings_dict['hotkeys']
            play_func = lambda *args: Thread(target=self.RCcontrol.play_indef, daemon=True).start()
            if shortcuts['Record']:    
                kb.add_hotkey(shortcuts['Record'], lambda *args: Thread(target = self.RCcontrol.record_and_save).start())
            if shortcuts['Play']:    
                kb.add_hotkey(shortcuts['Play'], play_func)
            if shortcuts['Save']:    
                kb.add_hotkey(shortcuts['Save'], self.RCcontrol.save_to_file)
            if shortcuts['Decrease Fpi']:    
                kb.add_hotkey(shortcuts['Decrease Fpi'], self.RCcontrol.decrease_speed)
            if shortcuts['Increase Fpi']:    
                kb.add_hotkey(shortcuts['Increase Fpi '], self.RCcontrol.increase_speed)
            if shortcuts['Increase Speed']:    
                kb.add_hotkey(shortcuts['Increase Speed'], self.RCcontrol.increase_speed_factor)
            if shortcuts['Decrease Speed']:
                kb.add_hotkey(shortcuts['Decrease Speed'], self.RCcontrol.decrease_speed_factor)
                
        screens = []
        start_thread     = Thread(target = get_start_view, args = [self.RCcontrol, self.settings_dict, screens], daemon=True)
        settings_thread  = Thread(target = get_settings_view, args = [self.settings_dict, update_settings, screens], daemon=True)
        view_thread      = Thread( target = get_view_view, args = [screens], daemon=True)
        filepath = self.settings_dict['interface']['Files Path']
        sequencer_thread = Thread(target = get_sequencer_view, args = [screens, self.RCcontrol, filepath], daemon=True)

        start_thread.run()
        settings_thread.run()
        view_thread.run()
        sequencer_thread.run()

        for _screen in screens:
            if _screen.name == 'start':
                start = _screen
                break

        self.RCcontrol.update_buttons = start.on_pre_enter     
        self.RCcontrol.filechooser= start.widgets['FileChooser']
        self.RCcontrol._play = start.watch['hotkeys'][('[b]Play[/b]', 'Play')]
        
        shortcuts = self.settings_dict['hotkeys']
        play_func = lambda *args: Thread(target=self.RCcontrol.play_indef, daemon=True).start()
        if shortcuts['Record']:    
            kb.add_hotkey(shortcuts['Record'], lambda *args: Thread(target = self.RCcontrol.record_and_save, daemon=True).start())
        if shortcuts['Play']:    
            kb.add_hotkey(shortcuts['Play'], play_func)
        if shortcuts['Save']:    
            kb.add_hotkey(shortcuts['Save'], self.RCcontrol.save_to_file)
        if shortcuts['Decrease Fpi']:    
            kb.add_hotkey(shortcuts['Decrease Fpi'], self.RCcontrol.decrease_speed)
        if shortcuts['Increase Fpi']:    
            kb.add_hotkey(shortcuts['Increase Fpi '], self.RCcontrol.increase_speed)
        if shortcuts['Increase Speed']:    
            kb.add_hotkey(shortcuts['Increase Speed'], self.RCcontrol.increase_speed_factor)
        if shortcuts['Decrease Speed']:
            kb.add_hotkey(shortcuts['Decrease Speed'], self.RCcontrol.decrease_speed_factor)


        _screen_manager = ScreenManager(transition=NoTransition())
        for _screen in screens:
            _screen_manager.add_widget(_screen)
       
         
        return _screen_manager

if __name__ == '__main__':
    state = kb.stash_state()
    KeyMouse_Sequencer().run()
    kb.restore_state(state)
    kb.unhook_all()