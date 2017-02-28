from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y


class DomViewer:
    """
    WARNING: SHOULDN'T USE THIS BECAUSE VERY SLOW FOR LARGE TEXT
    """

    def __init__(self, parent, dom_text):
        dlg = Toplevel(master=parent)

        text = Text(master=dlg)
        scroll = Scrollbar(dlg)
        scroll.pack(side=RIGHT, fill=Y)
        text.pack()
        scroll.config(command=text.yview)
        text.config(yscrollcommand=scroll.set)

        text.insert(1.0, dom_text)

        dlg.transient(parent)
        dlg.grab_set()
        parent.wait_window(dlg)
