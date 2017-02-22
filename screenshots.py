import os

from PIL import Image


def get_all_screenshot_names(directory):
    """

    :param directory: The directory where the screenshots are in
    :return: Filenames of all screenshots in the directory
    """

    # this assumes there are only screenshots in the dir
    all_files = os.listdir(directory)
    screenshots = []
    for f in all_files:
        if f.startswith('snapshot') and f.endswith('.png'):
            screenshots.append(f)

    return screenshots


def read_screenshot(path):
    return Image.open(path)