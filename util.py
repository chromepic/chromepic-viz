import os
import threading
from threading import Timer, Thread

import time


def immediate_subdirs(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def findnth(haystack, needle, n):
    parts = haystack.split(needle, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(haystack) - len(parts[-1]) - len(needle)


def extract_domain(url):
    i1 = findnth(url, '/', 1)
    i2 = findnth(url, '/', 2)
    if i1 == -1 or i2 == -1:
        return url
    return url[i1 + 1: i2]


def trunc(s, max_len):
    if len(s) <= max_len:
        return s
    else:
        return s[:max_len + 1] + ' ...'


# from http://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python
class RepeatedTimer(object):
    def __init__(self, function, *args, **kwargs):
        self._timer = None
        self.function = function
        self.args = args[0]
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.set_play_option('r1')

    def set_play_option(self, option):
        self.delay = (option[0], float(option[1:]))

    def _run(self):
        if self.is_running:
            if self.function():
                self._go()
        else:
            print('Stopped.')

    def _go(self):
        try:
            if self.args.current_index < len(self.args.metadata) - 2:
                if self.delay[0] == 'r':
                    # real time
                    t_diff_to_next = self.args.metadata[self.args.current_index + 1]['t'] \
                                     - self.args.metadata[self.args.current_index]['t']
                    t_diff_to_next /= self.delay[1]
                else:
                    # constant time
                    t_diff_to_next = self.delay[1]
                print('waiting {} seconds (current index is {})'.format(t_diff_to_next, self.args.current_index))
                self._timer = threading.Timer(t_diff_to_next, self._run)
                self._timer.start()
        except KeyError:
            pass

    def start(self):
        self.is_running = True
        self._go()

    def stop(self):
        self._timer.cancel()
        self.is_running = False
