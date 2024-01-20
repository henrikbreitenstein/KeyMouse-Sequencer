# KeyMouse Sequencer

Simple GUI for recording macros. One can record keyboard inputs and mouse inputs, together or separated, and play them back. Macros can be saved to file, and the files can be sequenced together to create more elaborate macros.

## Main Screen

![](https://github.com/henrikbreitenstein/KeyMouse-Sequencer/blob/main/images/main.PNG)

Record and play. Doubble click to load file from viewer to the right.

**Fpi**: Frames per iteration. If there are too many frames per second the speed won't do anything since python loops are so slow. To fix that we skip a number of frames per iteration instead. Only mouse movements are affected by this, as those fill up most of the frames.\
**Speed**: Factor of reduction of wait time between frames.

## View Screen

![](https://github.com/henrikbreitenstein/KeyMouse-Sequencer/blob/main/images/view.PNG)

Draw mouse movements and clicks of recorded macro. Edit with the start/end sliders and the cut button. You will have to redraw if you want to see the result.

## Sequencer Screen

![](https://github.com/henrikbreitenstein/KeyMouse-Sequencer/blob/main/images/sequencer.PNG)

Add files with the pluss buttons and type how many repeats of the given macro, then press save.

## To run

To run one would need the following

```
keyboard>=0.13.5
Kivy>=2.3.0
mouse>=0.7.1
numpy>=1.22.0
```

and in the main folder run the command

```
python3 ./gui.py
```

## Executable

The executable is in a ziped tarball in the dist folder.
