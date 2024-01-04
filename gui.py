import kivy
import json
import logging
import asyncio

import threading
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager, Screen

from RCcontrol import recorder
from pages.start_view import get_start_view
from pages.settings_view import get_settings_view
from pages.view_view import get_view_view
from pages.sequencer_view import get_sequencer_view

class KeyMouse_Seq(App):
    def build_config(self, config):
        config.setdefaults('mouse', {'disable_multitouch' : 'True'})

    def build(self):
        config = self.config
        start    = Screen( name = 'start' )
        settings = Screen( name= 'settings' )
        view     = Screen( name = 'view' )
        sequencer = Screen( name = 'sequencer' )
        
        _screen_manager = ScreenManager()
        _screen_manager.add_widget(start)
        _screen_manager.add_widget(settings)
        _screen_manager.add_widget(view)
        _screen_manager.add_widget(sequencer)
        

        with open('settings.json') as fjson:
            settings_dict = json.load(fjson)

        self.RCcontrol = recorder(settings_dict['controller'])
        
        start.add_widget(get_start_view(start, self.RCcontrol))
        settings.add_widget(get_settings_view(settings, self.RCcontrol, settings_dict))
        view.add_widget(get_view_view())
        sequencer.add_widget(get_sequencer_view())

        
        return _screen_manager

if __name__ == '__main__':   
    KeyMouse_Seq().run()
    