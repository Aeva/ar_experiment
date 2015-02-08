

import re
from sh import xwininfo, wmctrl


def get_window_ids():
    """
    Return a list of x11 window IDs managed by the window manager.
    """
    return [i.split(" ")[0] for i in wmctrl("-l").split("\n") if i.strip()]


def get_open_windows():
    """
    Returns a list of WindowInfo objects for all open windows.
    """
    return list(map(WindowInfo, get_window_ids()))


class WindowInfo(object):
    def __init__(self, window_id=None):
        cmd_options = ["-id", window_id]
        if not window_id:
            cmd_options = ["-root"]
        self.children = []
        self.window_id = hex(int(window_id, 16)) # strip leading 0s
        self._extract_info(cmd_options)

    def _extract_info(self, cmd_options):
        query = xwininfo(cmd_options)
        self.title = None
        self.width = None
        self.height = None
        self.x = None
        self.y = None
        for raw_line in query.split("\n"):
            line = raw_line.strip()
            if line.startswith("xwininfo:"):
                if self.window_id:
                    cut = line.split(self.window_id)[-1]
                    self.title = self._gen_title(cut.strip()[1:-1])
                else:
                    self.title = self._gen_title(None)

            elif line.startswith("-geometry"):
                nums = map(int, re.findall(r"[0-9]+", line.split(" ")[-1]))
                self.width, self.height, self.x, self.y = nums

    def _gen_title(self, window_title):
        if window_title is None:
            return "(the root window) (has no name)"
        elif window_title.count(" - Firefox"):
            return "Firefox"
        elif window_title.count(" emacs@"):
            return "Emacs"
        else:
            return window_title
