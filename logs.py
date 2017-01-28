import os
import tkinter

from PIL import Image


def get_all_screenshot_names(directory):
    """

    :param directory: The directory where the screenshots are in
    :return: Filenames of all screenshots in the directory
    """

    # this assumes there are only screenshots in the dir
    return os.listdir(directory)


def read_screenshot(path):
    return Image.open(path)
