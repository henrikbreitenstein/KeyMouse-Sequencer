from kivy.uix.screenmanager import Screen, ScreenManager
from typing import Callable
import numpy as np

def switch(_screen: Screen, to_screen_name: str) -> Callable:
    def switch_to(*args):
        _screen.manager.current = to_screen_name
    return switch_to
