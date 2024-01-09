from .imports import *
import mouse as ms
import numpy as np
from threading import Thread
from kivy.clock import mainthread
from collections import namedtuple

class view_screen(Screen):

    def __init__(self, layout, RCcontrol, draw, drawClicks):
        Screen.__init__(self)
        self.drawn_once = 0
        self.layout=layout
        self.RCcontrol = RCcontrol
        self.draw =draw
        self.drawClicks = drawClicks

    def on_enter(self):
        if len(self.RCcontrol.rec) > 10:
            if self.drawn_once == 0:
                time_line = [[]]
                points = [[]]
                self.draw(self.layout, self.RCcontrol.rec, time_line, points)
                self.drawClicks(self.layout, self.RCcontrol, time_line, points[0])
                self.drawn_once = 1

def draw(layout, recording, re_time_line, ret_points):
    
    if len(recording) < 10:
        Logger.info('Draw: Too small recording')
        return None
    
    points = []
    time_line = []

    for event in recording:
        if type(event) == ms._mouse_event.MoveEvent:
            points += [event.x, event.y]
            time_line.append(event.time)

    AO = 6 #Average over this many points
    points = np.array(points, dtype=np.float64)
    points[::2] -= np.min(points[::2])
    points[1::2] -= (np.min(points[1::2]))
    points[::2] /= (np.max(points[::2])/(0.9*layout.size[0]))
    points[1::2] /= np.max(points[1::2])/(0.9*layout.size[1])
    points[::2] += 0.05*layout.size[0]
    points[1::2] = layout.size[1] - points[1::2]
    points = list(points)

    @mainthread
    def call_to_main(layout, points):
        layout.canvas.after.clear()
        with layout.canvas.after:
            Color(1, 0, 0, 1)
            Line(points=points, width=1.0, force_custom_drawing_method=False)
        layout.canvas.ask_update()
    call_to_main(layout, points)
    ret_points[0] = points
    re_time_line[0] = time_line

def drawClicks(layout, RCcontrol, time_line, points):

    hold_time = 0
    circle_time = []
    circle_color = []
    lines = []

    for event in RCcontrol.rec:
        if type(event) == ms._mouse_event.ButtonEvent:
            match event.event_type:
                case 'down':
                    hold_time = event.time
                    circle_time.append(hold_time) 
                    circle_color.append((0, 1, 0, 1))
                case 'double':
                    hold_time = event.time
                    circle_time.append(hold_time)
                    circle_color.append((0, 0, 1, 1))
                case 'up':
                    lines.append(event.time)

    if len(circle_time) < 2:
        return None


    circle_time = np.array(circle_time)
    lines = np.array(lines)
    circle_time = np.argmin(
        abs(time_line - circle_time[:, None]),
        axis = 1
    )
    lines = np.argmin(
        abs(time_line - lines[:, None]),
        axis = 1
    )
    radius = 10
    for i in range(len(lines)):
        index = circle_time[i]
        circ_color = circle_color[i]
        start_pos =(points[2*index]-radius/2, points[2*index+1]-radius/2)
        _line = points[2*index:2*lines[i]]
        with layout.canvas.after:
            Color(rgba=circ_color)
            Line(points=_line, width=1.0, force_custom_drawing_method=False)
            Ellipse(
                pos=start_pos,
                size = (radius, radius))
            
    layout.canvas.ask_update()

def slider_points(layout, points, time_line, time_1, time_2, prev_lines):

    N_time = len(time_line)
    index_start = 2*(int(N_time*(time_1/100)))
    index_end = 2*(int(N_time*(time_2/100)))

    line_start = points[:index_start]
    line_end = points[index_end:]

    with layout.canvas.after:
        Color(1,0,0,1)  
        for _points in prev_lines[0]:
            Line(points=_points, width=1.0, force_custom_drawing_method=False)
        Color(0, 0, 0, 1)
        Line(points=line_start, width=1.0, force_custom_drawing_method=False)
        Line(points=line_end, width=1.0, force_custom_drawing_method=False)
    layout.canvas.ask_update()
    prev_lines[0] = [line_start, line_end]

def Cut(RCcontrol, ret_time_1, ret_time_2, grid, ret_time_line, ret_points, prev_lines):
    time_line = ret_time_line[0]
    if len(time_line) > 5:
        time_1 = ret_time_1[0]
        time_2 = ret_time_2[0]
        rec = np.array([event.time for event in RCcontrol.rec])
        k_rec = np.array([event.time for event in RCcontrol.k_rec])
        t_1_idx = int(len(time_line)*(time_1/101))
        t_2_idx = int(len(time_line)*(time_2/101))
        t_1 = time_line[t_1_idx]
        t_2 = time_line[t_2_idx]
        try:
            idx_1_rec  = np.argmin(abs(rec-t_1))
            idx_2_rec  = np.argmin(abs(rec-t_2))
            RCcontrol.rec = RCcontrol.rec[idx_1_rec:idx_2_rec]
            ret_time_line[0] = time_line[t_1_idx:t_2_idx]
        except:
            RCcontrol.rec = []
            ret_time_line[0] = []
        try:
            idx1_k = np.argmin(abs(k_rec-t_1))
            idx2_k = np.argmin(abs(k_rec-t_2))
            RCcontrol.k_rec = RCcontrol.k_rec[idx1_k:idx2_k]
            ret_points[0] = ret_points[0][2*t_1_idx:2*t_2_idx]
        except:
            RCcontrol.k_rec = []
            ret_points[0] = []

        prev_lines[0] = []

def get_view_view(screens):

    app = App.get_running_app()
    RCcontrol = app.RCcontrol

    view_layout = GridLayout(rows=3)
    
    widgets = {}

    ret_points = [[]]
    ret_time_line = [[]]
    DrawOnCanvas = FloatLayout()
    draw_button = Button(
        text='Draw',
        size_hint_x = None, 
        on_release=lambda *args: Thread(
            target = draw, 
            args=(DrawOnCanvas, RCcontrol.rec, ret_time_line, ret_points), 
            daemon=True).start()
    )

    drawClicks_btn = Button(
        text= 'Clicks',
        size_hint_x = None, 
        on_release = lambda *args: drawClicks(DrawOnCanvas, RCcontrol, ret_time_line[0], ret_points[0])
    )

    slidersGrid = GridLayout(rows=2, padding=5)
    slider1 = Slider(min=0, max=100, value=0, cursor_size=(20, 20), padding=10)
    slider2 = Slider(min=0, max=100, value=100, cursor_size=(20,20), padding=10)
    
    prev_lines = [[]]
    slider_on_move = lambda *args: slider_points(
        DrawOnCanvas,
        ret_points[0],
        ret_time_line[0],
        slider1.value,
        slider2.value,
        prev_lines
    )
    slider1.bind(on_touch_move=slider_on_move)
    slider2.bind(on_touch_move=slider_on_move)

    slidersGrid.add_widget(slider1)
    slidersGrid.add_widget(slider2)

    _screen = Screen()
    _screen.name = 'view'

    cut_button = Button(
        text = 'Cut',
        size_hint_x = None,
        on_release =lambda *args: Cut(
            RCcontrol,
            [slider1.value],
            [slider2.value],
            view_layout,
            ret_time_line,
            ret_points,
            prev_lines
        ))

    menu_buttons = [
        Button(text = 'Back',
            size_hint_x = None, 
            on_release=switch(_screen, 'start')),
        draw_button,
        drawClicks_btn,
        cut_button,
        slidersGrid
    ]
    
    taskbar = GridLayout(cols=len(menu_buttons), size_hint_y = None, height=30)
    for _button in menu_buttons:
        taskbar.add_widget(_button)
    
    view_layout.add_widget(DrawOnCanvas)
    view_layout.add_widget(taskbar)
    _screen.add_widget(view_layout)

    screens.append(_screen)