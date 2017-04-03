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
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False
