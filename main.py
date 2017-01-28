import os
import tkinter
from tkinter import Frame, X, BOTH, LEFT

import sys
from PIL import ImageTk

import logs


class LogViewer(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")

        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("Simple")
        self.pack(fill=BOTH, expand=True)

        screenshot_dir = '/Users/Valentin/OneDrive/School/Directed Study/vespa_log15/screenshots/11_8_2016__19_26_14_0x3fabb44008c0'
        all_screenshots = logs.get_all_screenshot_names(screenshot_dir)
        img1 = logs.read_screenshot(os.path.join(screenshot_dir, all_screenshots[0]))
        img2 = logs.read_screenshot(os.path.join(screenshot_dir, all_screenshots[1]))
        img3 = logs.read_screenshot(os.path.join(screenshot_dir, all_screenshots[2]))

        frame_ss = Frame(self)
        frame_ss.pack(side=LEFT, padx=5, pady=5)

        img1Label = tkinter.Label(frame_ss, image=img1, width=100)
        img1Label.pack(expand=True)


def main():
    root = tkinter.Tk()
    app = LogViewer(root)
    root.geometry("500x300+300+300")
    root.mainloop()


if __name__ == '__main__':
    main()
