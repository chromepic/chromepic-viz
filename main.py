import os
import tkinter
from tkinter import *

import sys

import PIL
import collections
from PIL import ImageTk, Image

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
        tab = '11_8_2016__18_41_58_0x35bb08c21c40'
        self.screenshot_dir = '/Users/Valentin/OneDrive/School/Directed Study/vespa_log14/screenshots/' + tab
        self.all_screenshots = logs.get_all_screenshot_names(self.screenshot_dir)

        metadata_all_tabs = logs.read_screenshot_metadata('/Users/valentin/OneDrive/School/Directed Study/vespa_log14/',
                                                          'vespa_log14.txt')
        # metadata just for this tab
        self.metadata = collections.defaultdict(dict)
        for m in metadata_all_tabs:
            if m['tab'] == tab:
                m['tk_img'] = None
                m['pil_img'] = None
                self.metadata[len(self.metadata)] = m
        # len of metadata might change because of dummy images
        self.n = len(self.metadata)

        # assuming they're named "snapshot_x.png"
        self.all_screenshots = sorted(self.all_screenshots, key=lambda x: int(x[9:-4]))

        self.marker = Image.open('marker.png')

    def init_snapshots(self):
        # for displaying the snapshots
        self.display_frames = [Frame(self) for _ in range(3)]
        self.displays = [Canvas(self.display_frames[i], bd=0, highlightthickness=0) for i in range(3)]
        # text labels
        self.display_labels = [Label(self.display_frames[i], text='') for i in range(3)]

        self.dummy_img = PIL.Image.new('RGBA', (1, 1), "white")

        self.switch_current_image(2)

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
        if self.metadata[img_i]['tk_img'].width() != width:  # it may already have been converted to correct size
            self.metadata[img_i]['tk_img'] = ImageTk.PhotoImage(
                self.resize_keep_aspect(width, self.metadata[img_i]['pil_img']))
        self.displays[canvas_i].delete("IMG")
        self.displays[canvas_i].create_image(0, 0, image=self.metadata[img_i]['tk_img'], anchor=NW, tags="IMG")

    def resize_keep_aspect(self, new_width, img):
        wpercent = (new_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        return img.resize((new_width, hsize), PIL.Image.ANTIALIAS)

    def init_navigation(self):
        self._job = None
        nav_frame = Frame(self)
        nav_frame.grid(row=3, column=0, columnspan=4, padx=0, pady=0, sticky=N + S + E + W)
        self.prev = Button(nav_frame, text="<", command=lambda: self.on_switch_image(self.current_index))
        self.prev.pack(side=LEFT)
        self.next = Button(nav_frame, text=">", command=lambda: self.on_switch_image(self.current_index + 2))
        self.next.pack(side=RIGHT)
        self.w = Scale(nav_frame, from_=1, to=self.n, orient=HORIZONTAL,
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

        index = int(index) - 1
        self.current_index = index

        if hasattr(self, 'prev'):
            self.prev['state'] = 'normal'
            self.next['state'] = 'normal'

            if index == 0:
                self.prev['state'] = 'disabled'
            if index == self.n - 1:
                self.next['state'] = 'disabled'

        if hasattr(self, 'w'):
            self.w.set(index + 1)

        for i in range(index - 1, index + 2):
            if not (-1 <= i <= self.n + 1):
                # out of bounds
                continue

            # load lazily
            if not hasattr(self.metadata[i], 'pil_img') or self.metadata[i]['pil_img'] is None:
                # img not loaded yet
                if i < 0 or i >= self.n or self.metadata[i]['fname'] not in self.all_screenshots:
                    # dummy image at index=0 to prevent index out of bounds
                    pil_img = self.dummy_img
                else:
                    pil_img = logs.read_screenshot(os.path.join(self.screenshot_dir, self.metadata[i]['fname']))
                    pil_img = pil_img.copy()
                    mouse_x, mouse_y = self.metadata[i]['mouse'][0], self.metadata[i]['mouse'][1]
                    pil_img.paste(self.marker.copy(), (mouse_x, mouse_y))

                self.metadata[i]['pil_img'] = pil_img
                self.metadata[i]['tk_img'] = ImageTk.PhotoImage(pil_img)

            canvas_i = i - index + 1
            self.resize(canvas_i, max(100, self.displays[canvas_i].winfo_width()))
            if 0 <= i < self.n:
                self.display_labels[canvas_i]['text'] = self.metadata[i]['fname']
                if i == index and hasattr(self, 'event_detail'):
                    if self.metadata[i]['trigger'].lower() == 'key':
                        self.event_detail['text'] = 'Last key pressed: ' + str(self.metadata[i]['key'])
                    else:
                        self.event_detail['text'] = 'Last mouse pos: ({}, {})'.format(
                            self.metadata[i]['mouse'][0],
                            self.metadata[i]['mouse'][1])
                    self.trigger_label['text'] = 'Trigger: ' + str(self.metadata[i]['trigger'])
                    self.time_label['text'] = 'Time: {0:.1f} seconds'.format(self.metadata[i]['t'])
            else:
                self.display_labels[canvas_i]['text'] = ''

    def init_metadata(self):
        metadata_frame = Frame(self)
        metadata_frame.grid(row=5, column=0, columnspan=4, padx=0, pady=0, sticky=N + S + E + W)

        self.trigger_label = Label(metadata_frame, text='')
        self.trigger_label.pack()

        self.event_detail = Label(metadata_frame, text='')
        self.event_detail.pack()

        self.time_label = Label(metadata_frame, text='')
        self.time_label.pack()


def main():
    root = tkinter.Tk()
    app = LogViewer(root)
    wh_ratio = 1.9
    width = 1200
    height = int(width / wh_ratio)
    root.geometry("{}x{}+100+100".format(width, height))
    root.mainloop()


if __name__ == '__main__':
    main()
