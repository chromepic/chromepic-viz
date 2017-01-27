import os
import tkinter

import sys
from PIL import ImageTk

import logs


class LogViewer(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, background="white")

        self.parent = parent

        self.initUI()

    def initUI(self):
        self.parent.title("Simple")
        self.pack(fill=tkinter.BOTH, expand=1)


def main():
    root = tkinter.Tk()
    app = LogViewer(root)
    root.geometry("250x150+300+300")

    screenshot_dir = '/Users/Valentin/OneDrive/School/Directed Study/vespa_log15/screenshots/11_8_2016__19_26_14_0x3fabb44008c0'
    all_screenshots = logs.get_all_screenshot_names(screenshot_dir)
    img = logs.read_screenshot(os.path.join(screenshot_dir, all_screenshots[0]))
    panel = tkinter.Label(root, image=img)
    panel.pack(side="bottom", fill="both", expand="yes")

    root.mainloop()


if __name__ == '__main__':
    main()
