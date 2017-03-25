import os
import subprocess
import tkinter
from tempfile import mkdtemp
from tkinter import *

import sys

import PIL
import collections

import shutil
from PIL import ImageTk, Image

import doms
import logs
import screenshots
import triggers
import util
from dom_viewer import DomViewer
from sys import platform as _platform

import argparse


class LogViewer(Frame):
    def __init__(self, parent, dir):
        Frame.__init__(self, parent, background="white")

        self.base_dir = dir
        self.parent = parent
        self.init_ui()

    def cleanup(self):
        print('Cleaning up...')
        shutil.rmtree(self.tmp_dir)
        self.parent.destroy()

    def init_ui(self):
        self.parent.title("ChromePic Viewer")
        self.pack(fill=BOTH, expand=True)
        self.grid_columnconfigure(0, weight=1)

        self.load_data()
        self.init_menu_bar()
        self.switch_to_tab('All')
        self.init_snapshots()
        self.init_navigation()
        self.init_metadata()

    def get_all_tabs(self):
        all_tabs = set(util.immediate_subdirs(os.path.join(self.base_dir, 'screenshots')))
        # all_tabs |= set(util.immediate_subdirs(os.path.join(self.base_dir, 'dom_snapshots')))
        return sorted(list(all_tabs))

    def load_data(self):
        log_name = self.base_dir.split('/')[-1]
        self.all_tabs = self.get_all_tabs()

        self.metadata_all_tabs, self.tab_to_url = logs.read_screenshot_metadata(self.base_dir,
                                                                                log_name + '.txt')

        self.marker = Image.open('marker.png')

        self.tmp_dir = mkdtemp()

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
        self.nav_frame = Frame(self)
        self.nav_frame.grid(row=3, column=0, columnspan=4, padx=0, pady=0, sticky=N + S + E + W)
        self.prev = Button(self.nav_frame, text="<", command=lambda: self.on_switch_image(self.current_index))
        self.prev.pack(side=LEFT)
        self.next = Button(self.nav_frame, text=">", command=lambda: self.on_switch_image(self.current_index + 2))
        self.next.pack(side=RIGHT)
        self.w = Scale(self.nav_frame, from_=1, to=self.n, orient=HORIZONTAL,
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
                    pil_img = screenshots.read_screenshot(
                        os.path.join(self.base_dir, 'screenshots', self.metadata[i]['fname']))
                    # only show mouse marker on events triggered by mouse
                    if self.metadata[i]['trigger'] in triggers.mouse_position_triggers:
                        pil_img = pil_img.copy()
                        mouse_x, mouse_y = self.metadata[i]['mouse'][0], self.metadata[i]['mouse'][1]
                        pil_img.paste(self.marker.copy(), (mouse_x, mouse_y))

                self.metadata[i]['pil_img'] = pil_img
                self.metadata[i]['tk_img'] = ImageTk.PhotoImage(pil_img)

            canvas_i = i - index + 1
            self.resize(canvas_i, max(100, self.displays[canvas_i].winfo_width()))
            if 0 <= i < self.n:
                self.display_labels[canvas_i]['text'] = self.metadata[i]['fname'].split('/')[-1]
                if i == index and hasattr(self, 'event_detail'):
                    if self.metadata[i]['trigger'] in triggers.keycode_triggers:
                        self.event_detail['text'] = 'Last key pressed: ' + str(self.metadata[i]['key'])
                    elif self.metadata[i]['trigger'] in triggers.mouse_position_triggers:
                        self.event_detail['text'] = 'Last mouse pos: ({}, {})'.format(
                            self.metadata[i]['mouse'][0],
                            self.metadata[i]['mouse'][1])
                    self.trigger_label['text'] = 'Trigger: ' + str(self.metadata[i]['trigger'])
                    self.tab_label['text'] = 'Tab: ' + self.metadata[i]['tab']

                    if self.metadata[i]['abstime'] is None:
                        self.time_label['text'] = 'Time: Error'
                    else:
                        date_str = self.metadata[i]['abstime'].strftime('%m/%d/%Y %H:%M:%S')
                        self.time_label['text'] = 'Time: ' + date_str
            else:
                self.display_labels[canvas_i]['text'] = ''

    def init_metadata(self):
        metadata_frame = Frame(self)

        metadata_frame.grid(row=5, column=0, columnspan=4, padx=0, pady=0, sticky=N + S + E + W)

        self.tab_label = Label(metadata_frame, text='')
        self.tab_label.pack()

        self.trigger_label = Label(metadata_frame, text='')
        self.trigger_label.pack()

        self.event_detail = Label(metadata_frame, text='')
        self.event_detail.pack()

        self.time_label = Label(metadata_frame, text='')
        self.time_label.pack()

        self.dom_button = Button(metadata_frame, text='Show DOM text', command=self.show_dom)
        self.dom_button.pack()

        self.dom_explorer_button = Button(metadata_frame, text='Show DOM in explorer ', command=self.show_dom_explorer)
        self.dom_explorer_button.pack()

    def show_dom(self):
        path = os.path.join(self.base_dir, 'dom_snapshots', self.metadata[self.current_index]['dom'])
        dom = doms.read_dom(path)
        # write to temporary file
        fname = '(text only) ' + self.metadata[self.current_index]['tab'] + ': ' \
                + self.metadata[self.current_index]['dom'].split('/')[-1][:-5] + 'txt'
        temp_path = doms.write_to_temp(dom, fname, self.tmp_dir)

        if _platform == 'linux' or _platform == 'linux2':
            # linux
            subprocess.call(['xdg-open', temp_path])
        elif _platform == 'darwin':
            # MAC OS X
            subprocess.call(['open', temp_path])
        elif _platform == 'win32':
            # Windows
            subprocess.call([temp_path])

    def show_dom_explorer(self):
        file_path = os.path.join(self.base_dir, 'dom_snapshots', self.metadata[self.current_index]['dom'])
        folder_path = os.path.dirname(file_path)

        if _platform == 'linux' or _platform == 'linux2':
            # linux: select file in file browser
            subprocess.call(['nautilus', file_path])
        elif _platform == 'darwin':
            # MAC OS X
            subprocess.call(['open', '--', folder_path])
        elif _platform == 'win32':
            # Windows
            os.startfile(folder_path)

    def init_menu_bar(self):
        self.menubar = Menu(self)

        self.tab_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tab", menu=self.tab_menu)
        self.vlevel = IntVar()

        # all tabs
        self.tab_menu.add_radiobutton(label='All', var=self.vlevel, value=0,
                                      command=lambda: self.switch_to_tab('All'))

        for i, tab in enumerate(self.all_tabs):
            t = tab
            label = self.tab_to_url[tab]
            label = util.extract_domain(label)
            self.tab_menu.add_radiobutton(label=label, var=self.vlevel, value=i + 1,
                                          command=lambda: self.switch_to_tab(self.all_tabs[self.vlevel.get() - 1]))

        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            # master is a toplevel window (Python 1.4/Tkinter 1.63)
            self.master.tk.call(self.parent, "config", "-menu", self.menubar)

    def switch_to_tab(self, tab_name):
        print('Switching to tab ' + tab_name)
        self.tab = tab_name
        if self.tab == 'All':
            self.all_screenshots = []
            for t in self.all_tabs:
                additional_screenshots = screenshots.get_all_screenshot_names(
                    os.path.join(self.base_dir, 'screenshots', t))
                for i in range(len(additional_screenshots)):
                    additional_screenshots[i] = os.path.join(t, additional_screenshots[i])
                self.all_screenshots += additional_screenshots

        else:
            self.all_screenshots = screenshots.get_all_screenshot_names(
                os.path.join(self.base_dir, 'screenshots', self.tab))
            for i in range(len(self.all_screenshots)):
                self.all_screenshots[i] = os.path.join(self.tab, self.all_screenshots[i])

        # assuming they're named "tab/snapshot_x.png"
        self.all_screenshots = sorted(self.all_screenshots, key=lambda x: int(x[x.rfind('_') + 1:-4]))

        if hasattr(self, 'metadata'):
            if 't' in self.metadata[self.current_index]:
                old_time = self.metadata[self.current_index]['t']
            else:
                old_time = 0
        else:
            old_time = 0

        # metadata just for this tab
        self.metadata = collections.defaultdict(dict)
        for m in self.metadata_all_tabs:
            if self.tab == 'All' or m['tab'] == self.tab:
                m['tk_img'] = None
                m['pil_img'] = None
                self.metadata[len(self.metadata)] = m
        # len of metadata might change because of dummy images
        self.n = len(self.metadata)

        if hasattr(self, 'w'):
            self.w.config(to=self.n)
            index = 0  # logs.time_closest(self.metadata, old_time)   <-- Uncomment to jump to nearest time. Still has bug though.
            self.switch_current_image(index + 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', metavar='directory', type=str,
                        help='Directory in which the log text file is contained, '
                             'along with the screenshots and dom_snapshots directories.')
    args = parser.parse_args()
    dir = args.dir
    print('Dir: ' + dir)

    root = tkinter.Tk()
    root.tk_setPalette(background='white')
    app = LogViewer(root, dir)
    wh_ratio = 1.5
    width = 1200
    height = int(width / wh_ratio)
    root.geometry("{}x{}+100+100".format(width, height))
    root.protocol("WM_DELETE_WINDOW", app.cleanup)
    root.mainloop()


if __name__ == '__main__':
    main()
