# Usage

Simply call 'python3 main.py [log dir]'

# Dependencies

- <b>Python 3</b>
- <b>PIL</b> (python imaging library)
- <b>tkinter 8.6</b>. It's important to be on version 8.6, not 8.5, otherwise PNG images might not be displayed correctly. On Ubuntu, I had version 8.6 out of the box, on Mac OS it was 8.5, but check for yourself! You can run 'import tkinter' and then 'tkinter.TkVersion' or 'tkinter.TclVersion' to check your version.

Under Ubuntu, these can be installed as follows:

sudo apt-get install python3-tk
sudo apt-get install libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev
sudo pip3 install Pillow

