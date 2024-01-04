import json

controller = {
    'Speed' : 5,
    'Speed_interval' : 1,
    'Factor': 1,
    'Factor_interval' : 0.1
}

hotkeys = {
    'Record' : 'ctrl+r',
    'Stop recording' : 'ctrl+p',
    'Save' : '',
    'Load' : '',
    'Increase Fpi ' : '',
    'Decrease Fpi' : '',
    'Set Fpi' : '',
    'Increase replay speed' : '',
    'Decrease replay speed' : '',
    'Set replay speed' : '',
    'View' : '',
    'Sequencer' : '',
    'Settings' : '' 
}

interface = {
    'Font size' : '10',
    'Animations' : 'On',
}

settings = {
    'controller' : controller,
    'hotkeys' : hotkeys,
    'interface' : interface
} 

with open('settings.json', 'w') as fp:
    json.dump(settings, fp)