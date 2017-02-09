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

        self.load_data()
        self.init_snapshots()
        self.init_navigation()
        self.init_metadata()

    def load_data(self):
        tab = '11_8_2016__19_26_14_0x3fabb44008c0'
        self.screenshot_dir = '/Users/Valentin/OneDrive/School/Directed Study/vespa_log15/screenshots/' + tab
        self.all_screenshots = logs.get_all_screenshot_names(self.screenshot_dir)

        metadata_all_tabs = logs.read_screenshot_metadata('/Users/valentin/OneDrive/School/Directed Study/vespa_log15/',
                                                          'vespa_log15.txt')
        # metadata just for this tab
        self.metadata = []
        for m in metadata_all_tabs:
            if m[2] == tab:
                self.metadata.append(m)

        # assuming they're named "snapshot_x.png"
        self.all_screenshots = sorted(self.all_screenshots, key=lambda x: int(x[9:-4]))

    def init_snapshots(self):
        self.pil_imgs = {}
        # to keep them from getting deleted by garbage collection
        self.tk_imgs = {}

        # for displaying the snapshots
        self.display_frames = [Frame(self) for _ in range(3)]
        self.displays = [Canvas(self.display_frames[i], bd=0, highlightthickness=0) for i in range(3)]
        # text labels
        self.display_labels = [Label(self.display_frames[i], text='') for i in range(3)]

        self.dummy_img = PIL.Image.new('RGBA', (1, 1), "white")

        self.switch_current_image(1)

        self.resizing_methods = []
        self.resizing_methods.append(lambda event: self.resize(0, event.width))
        self.resizing_methods.append(lambda event: self.resize(1, event.width))
        self.resizing_methods.append(lambda event: self.resize(2, event.width))

        for i in range(3):
            self.displays[i].bind("<Configure>", self.resizing_methods[i])

        padx, pady = 20, 20
        # previous
        self.display_frames[0].grid(row=0, column=3, columnspan=1, rowspan=1, padx=padx, pady=pady,
                                    sticky=N + S + E + W)
        # current
        self.display_frames[1].grid(row=0, column=0, columnspan=2, rowspan=2, padx=padx, pady=pady,
                                    sticky=N + S + E + W)
        # next
        self.display_frames[2].grid(row=1, column=3, columnspan=1, rowspan=1, padx=padx, sticky=N + S + E + W)

        for i in range(3):
            self.display_labels[i].pack()
            self.display_labels[i].config(font=("Arial", 18))

        for i in range(3):
            self.displays[i].pack(fill=BOTH, expand=True)

    def resize(self, canvas_i, width):
        img_i = canvas_i + self.current_index - 1
        if self.tk_imgs[img_i].width() != width:  # it may already have been converted to correct size
            self.tk_imgs[img_i] = ImageTk.PhotoImage(self.resize_keep_aspect(width, self.pil_imgs[img_i]))
        self.displays[canvas_i].delete("IMG")
        self.displays[canvas_i].create_image(0, 0, image=self.tk_imgs[img_i], anchor=NW, tags="IMG")

    def resize_keep_aspect(self, new_width, img):
        wpercent = (new_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        return img.resize((new_width, hsize), PIL.Image.ANTIALIAS)

    def init_navigation(self):
        self._job = None
        nav_frame = Frame(self)
        nav_frame.grid(row=3, column=0, columnspan=4, padx=0, pady=0, sticky=N + S + E + W)
        self.prev = Button(nav_frame, text="<", command=lambda: self.on_switch_image(self.current_index - 1))
        self.prev.pack(side=LEFT)
        self.next = Button(nav_frame, text=">", command=lambda: self.on_switch_image(self.current_index + 1))
        self.next.pack(side=RIGHT)
        self.w = Scale(nav_frame, from_=1, to=len(self.metadata), orient=HORIZONTAL,
                       command=self.on_switch_image)
        self.w.pack(expand=True, fill=BOTH)

    def on_switch_image(self, index):
        # this logic makes the image switch only if a certain amount of time has elapsed since the last scale change,
        # for performance reasons.
        # (see http://stackoverflow.com/questions/3966303/tkinter-slider-how-to-trigger-the-event-only-when-the-iteraction-is-complete)

        if self._job:
            self.parent.after_cancel(self._job)
        delay = 100
        self._job = self.parent.after(delay, self.switch_current_image, index)

    def switch_current_image(self, index):
        self._job = None

        index = int(index)
        self.current_index = index

        if hasattr(self, 'prev'):
            self.prev['state'] = 'normal'
            self.next['state'] = 'normal'

            if index == 1:
                self.prev['state'] = 'disabled'
            if index == len(self.metadata):
                self.next['state'] = 'disabled'

        if hasattr(self, 'w'):
            self.w.set(index)

        for i in range(index - 1, index + 2):
            if not (0 <= i <= len(self.metadata) + 1):
                # out of bounds
                continue

            # load lazily
            if i not in self.pil_imgs:
                # img not loaded yet
                if i == 0 or i == len(self.metadata) + 1 or self.metadata[i - 1][1] not in self.all_screenshots:
                    # dummy image at index=0 to prevent index out of bounds
                    pil_img = self.dummy_img
                else:
                    pil_img = logs.read_screenshot(os.path.join(self.screenshot_dir, self.metadata[i - 1][1]))

                self.pil_imgs[i] = pil_img
                self.tk_imgs[i] = ImageTk.PhotoImage(pil_img)

            canvas_i = i - index + 1
            self.resize(canvas_i, max(100, self.displays[canvas_i].winfo_width()))
            if 0 <= i - 1 < len(self.metadata):
                self.display_labels[canvas_i]['text'] = self.metadata[i - 1][1]
                if hasattr(self, 'last_key_label'):
                    self.last_key_label['text'] = 'Last key pressed: ' + str(self.metadata[i - 1][5])
                    self.trigger_label['text'] = 'Trigger: ' + str(self.metadata[i - 1][6])
                    self.time_label['text'] = 'Time: {0:.1f} seconds'.format(self.metadata[i - 1][3])
            else:
                self.display_labels[canvas_i]['text'] = ''



    def init_metadata(self):
        metadata_frame = Frame(self)
        metadata_frame.grid(row=5, column=0, columnspan=4, padx=0, pady=0, sticky=N + S + E + W)

        self.last_key_label = Label(metadata_frame, text='last key: X')
        self.last_key_label.pack()

        self.trigger_label = Label(metadata_frame, text='trigger: mouse click')
        self.trigger_label.pack()

        self.time_label = Label(metadata_frame, text='time: 12.3s')
        self.time_label.pack()


def main():
    root = tkinter.Tk()
    app = LogViewer(root)
    wh_ratio = 2
    width = 1200
    height = int(width / wh_ratio)
    root.geometry("{}x{}+100+100".format(width, height))
    root.mainloop()


if __name__ == '__main__':
    main()
