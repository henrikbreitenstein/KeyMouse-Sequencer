import keyboard as kb
import mouse as ms

def help(shortcuts):
    print("""
        kb.add_hotkey('ctrl+r', RCcontrol.record_and_save)
          
            - Starts recording and sets it ats the current play file

        kb.add_hotkey('ctrl+p', RCcontrol.play_indef)
          
            - Plays the current play file until it encounters 'alt' at the beginning.
          
        """)

def init_keys(RCcontrol, shortcuts):
    kb.add_hotkey('ctrl+r', RCcontrol.record_and_save)
    kb.add_hotkey('ctrl+p', RCcontrol.play_indef)
    kb.add_hotkey('ctrl+s', RCcontrol.save_to_file)
    kb.add_hotkey('ctrl+l', RCcontrol.load_from_file)
    kb.add_hotkey('ctrl+j', RCcontrol.decrease_speed)
    kb.add_hotkey('ctrl+k', RCcontrol.increase_speed)
    kb.add_hotkey('ctrl+i', RCcontrol.list_clicks)
    kb.add_hotkey('ctrl+e', RCcontrol.remove_click)
    kb.add_hotkey('ctrl+t', RCcontrol.set_speed)
    kb.add_hotkey('ctrl+d', RCcontrol.define_speed)
    kb.add_hotkey('ctrl+u', RCcontrol.set_factor)
    kb.add_hotkey('ctrl+y', RCcontrol.combine)
    kb.add_hotkey('ctrl+h', help(shortcuts))
    kb.wait()