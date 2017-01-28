import os
import tkinter
from tkinter import *

import sys

import PIL
from PIL import ImageTk

import logs


class LogViewer(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")

        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.parent.title("Simple")
        self.pack(fill=BOTH, expand=True)

        screenshot_dir = '/Users/Valentin/OneDrive/School/Directed Study/vespa_log15/screenshots/11_8_2016__19_26_14_0x3fabb44008c0'
        all_screenshots = logs.get_all_screenshot_names(screenshot_dir)

        self.pil_imgs = [None for _ in range(3)]
        # to keep them from getting deleted by garbage collection
        self.tk_imgs = [None for _ in range(3)]

        self.displays = [Canvas(self, bd=0, highlightthickness=0) for _ in range(3)]

        for i in range(3):
            pil_img = logs.read_screenshot(os.path.join(screenshot_dir, all_screenshots[i]))
            self.pil_imgs[i] = pil_img
            self.tk_imgs[i] = ImageTk.PhotoImage(pil_img)

        self.displays[0].create_image(0, 0, image=self.tk_imgs[0], anchor=NW, tags="IMG")
        self.displays[0].pack(fill=BOTH, expand=True)

        self.displays[0].bind("<Configure>", self.resize)

    def resize(self, event):
        canvas_i = 0
        self.tk_imgs[canvas_i] = ImageTk.PhotoImage(self.resize_keep_aspect(event.width, self.pil_imgs[canvas_i]))
        self.displays[canvas_i].delete("IMG")
        self.displays[canvas_i].create_image(0, 0, image=self.tk_imgs[canvas_i], anchor=NW, tags="IMG")

    def resize_keep_aspect(self, new_width, img):
        wpercent = (new_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        return img.resize((new_width, hsize), PIL.Image.ANTIALIAS)


def main():
    root = tkinter.Tk()
    app = LogViewer(root)
    root.geometry("500x300+300+300")
    root.mainloop()


if __name__ == '__main__':
    main()
