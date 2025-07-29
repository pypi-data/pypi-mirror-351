# -*- coding: utf-8 -*-
import sys

__version__ = "3.3.2"

# First install USER_THEMES
from ChatRoom.gui_config import USER_THEMES
from ttkbootstrap.themes import user
user.USER_THEMES.update(USER_THEMES)

import cprint  # noqa: E402
from ChatRoom.main import Room, User  # noqa: E402, F401
# from ChatRoom.net import Server, Client
from ChatRoom.tools import hash_encryption  # noqa: E402, F401
from ChatRoom.Launcher import Launcher  # noqa: E402, F401
# from ChatRoom.gui import RunRoom as _RunRoom

log = encrypt = main = net = sys = gui = sysinfo = cprint = launcher = package = tools = config = gui_config = user = USER_THEMES = None  # noqa: F811
del log, encrypt, main, net, sys, gui, sysinfo, cprint, launcher, package, tools, config, gui_config, user, USER_THEMES