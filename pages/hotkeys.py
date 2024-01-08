import keyboard as kb
import mouse as ms
from threading import Thread

def init_keys(RCcontrol, shortcuts):
    kb.unhook_all_hotkeys()
    play_func = lambda *args: Thread(target=RCcontrol.play_indef, daemon=True).start()
    if shortcuts['Record']:    
        kb.add_hotkey(shortcuts['Record'], lambda *args: Thread(target = RCcontrol.record_and_save, daemon=True).start())
    if shortcuts['Play']:    
        kb.add_hotkey(shortcuts['Play'], play_func)
    if shortcuts['Save']:    
        kb.add_hotkey(shortcuts['Save'], RCcontrol.save_to_file)
    if shortcuts['Decrease Fpi']:    
        kb.add_hotkey(shortcuts['Decrease Fpi'], RCcontrol.decrease_speed)
    if shortcuts['Increase Fpi']:    
        kb.add_hotkey(shortcuts['Increase Fpi '], RCcontrol.increase_speed)
    if shortcuts['Increase Speed']:    
        kb.add_hotkey(shortcuts['Increase Speed'], RCcontrol.increase_speed_factor)
    if shortcuts['Decrease Speed']:
        kb.add_hotkey(shortcuts['Decrease Speed'], RCcontrol.decrease_speed_factor)
