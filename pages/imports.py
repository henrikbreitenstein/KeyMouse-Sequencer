import time

from typing import Callable
from functools import partial
from multiprocessing.managers import SyncManager

from kivy.animation import Animation
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.graphics import *

from .utils import switch


