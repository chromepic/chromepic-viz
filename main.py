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

        self.grid_columnconfigure(0, weight=1)

        screenshot_dir = '/Users/Valentin/OneDrive/School/Directed Study/vespa_log15/screenshots/11_8_2016__19_26_14_0x3fabb44008c0'
        all_screenshots = logs.get_all_screenshot_names(screenshot_dir)

        self.pil_imgs = [None for _ in range(3)]
        # to keep them from getting deleted by garbage collection
        self.tk_imgs = [None for _ in range(3)]

        # read snapshots
        for i in range(3):
            pil_img = logs.read_screenshot(os.path.join(screenshot_dir, all_screenshots[i]))
            self.pil_imgs[i] = pil_img
            self.tk_imgs[i] = ImageTk.PhotoImage(pil_img)

        # for displaying the snapshots
        self.displays = [Canvas(self, bd=0, highlightthickness=0) for _ in range(3)]

        self.resizing_methods = []
        self.resizing_methods.append(lambda event: self.resize(0, event))
        self.resizing_methods.append(lambda event: self.resize(1, event))
        self.resizing_methods.append(lambda event: self.resize(2, event))

        for i in range(3):
            self.displays[i].create_image(0, 0, image=self.tk_imgs[i], anchor=NW, tags="IMG")
            self.displays[i].bind("<Configure>", self.resizing_methods[i])

        padx, pady = 20, 20
        self.displays[0].grid(row=0, column=0, columnspan=2, rowspan=2, padx=padx, pady=pady, sticky=N + S + E + W)
        self.displays[1].grid(row=0, column=3, columnspan=1, rowspan=1, padx=padx, pady=pady, sticky=N + S + E + W)
        self.displays[2].grid(row=1, column=3, columnspan=1, rowspan=1, padx=padx, sticky=N + S + E + W)

    def resize(self, canvas_i, event):
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
    root.geometry("1000x550+200+200")
    root.mainloop()


if __name__ == '__main__':
    main()
