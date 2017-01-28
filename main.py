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
        self.parent.title("ChromePic Viewer")
        self.pack(fill=BOTH, expand=True)
        self.grid_columnconfigure(0, weight=1)

        self.init_snapshots()

        self.init_navigation()

    def init_snapshots(self):
        self.screenshot_dir = '/Users/Valentin/OneDrive/School/Directed Study/vespa_log15/screenshots/11_8_2016__19_26_14_0x3fabb44008c0'
        self.all_screenshots = logs.get_all_screenshot_names(self.screenshot_dir)

        self.pil_imgs = {}
        # to keep them from getting deleted by garbage collection
        self.tk_imgs = {}

        # for displaying the snapshots
        self.display_frames = [Frame()]
        self.displays = [Canvas(self, bd=0, highlightthickness=0) for _ in range(3)]

        self.dummy_img = PIL.Image.new('RGB', (1, 1))

        self.switch_current_image(1)

        self.resizing_methods = []
        self.resizing_methods.append(lambda event: self.resize(0, event))
        self.resizing_methods.append(lambda event: self.resize(1, event))
        self.resizing_methods.append(lambda event: self.resize(2, event))

        for i in range(3):
            self.displays[i].bind("<Configure>", self.resizing_methods[i])

        padx, pady = 20, 20
        self.displays[0].grid(row=0, column=0, columnspan=2, rowspan=2, padx=padx, pady=pady, sticky=N + S + E + W)
        self.displays[1].grid(row=0, column=3, columnspan=1, rowspan=1, padx=padx, pady=pady, sticky=N + S + E + W)
        self.displays[2].grid(row=1, column=3, columnspan=1, rowspan=1, padx=padx, sticky=N + S + E + W)

    def resize(self, canvas_i, event):
        img_i = canvas_i + self.current_index - 1
        self.tk_imgs[img_i] = ImageTk.PhotoImage(self.resize_keep_aspect(event.width, self.pil_imgs[img_i]))
        self.displays[canvas_i].delete("IMG")
        self.displays[canvas_i].create_image(0, 0, image=self.tk_imgs[img_i], anchor=NW, tags="IMG")

    def resize_keep_aspect(self, new_width, img):
        wpercent = (new_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        return img.resize((new_width, hsize), PIL.Image.ANTIALIAS)

    def init_navigation(self):
        w = Scale(self, from_=1, to=len(self.all_screenshots), orient=HORIZONTAL, command=self.switch_current_image)
        w.grid(row=3, column=0, columnspan=4, padx=20, pady=20, sticky=N + S + E + W)

    def switch_current_image(self, index):
        index = int(index)
        self.current_index = index
        for i in range(index - 1, index + 2):
            if not (0 <= i <= len(self.all_screenshots)):
                # out of bounds
                continue

            if i not in self.pil_imgs:
                # img not loaded yet
                if i == 0:
                    # dummy image at index=0 to prevent index out of bounds
                    pil_img = self.dummy_img
                else:
                    pil_img = logs.read_screenshot(os.path.join(self.screenshot_dir, self.all_screenshots[i - 1]))
            else:
                pil_img = self.pil_imgs[i]

            self.pil_imgs[i] = pil_img
            self.tk_imgs[i] = ImageTk.PhotoImage(pil_img)
            canvas_i = i - index + 1
            self.displays[canvas_i].create_image(0, 0, image=self.tk_imgs[i], anchor=NW, tags="IMG")


def main():
    root = tkinter.Tk()
    app = LogViewer(root)
    hw_ratio = 1.907801
    width = 1100
    height = int(width / hw_ratio)
    root.geometry("{}x{}+200+200".format(width, height))
    root.mainloop()


if __name__ == '__main__':
    main()
