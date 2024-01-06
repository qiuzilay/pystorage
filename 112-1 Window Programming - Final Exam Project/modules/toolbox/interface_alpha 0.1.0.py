from io import StringIO
import sys

sys.stdout = logs = StringIO()

from os import chdir, getcwd
from os.path import dirname, realpath
from typing import Any
from collections import namedtuple
from dataclasses import dataclass, field
from threading import Thread
from queue import Queue
from time import sleep
import tkinter as tk

@dataclass
class path:
    icon: str

if __name__.__eq__('__main__'):
    chdir(dirname(realpath(__file__)))
    from gadget import Gadget
    from arraylist import array
    from console import console
    from bases import Enum
    path = path(icon = './images/icon.ico')
else:
    try:
        from toolbox import Gadget, array, Enum, console # @IgnoreException
        path = path(icon = './toolbox/images/icon.ico')
    except ImportError:
        from modules.toolbox import Gadget, array, Enum, console
        path = path(icon = './modules/toolbox/images/icon.ico')

class color(Enum):
    white = '#FFFFFF'
    black = '#000000'

class ControlPanel:

    def __new__(cls, *args, **kwargs):

        @dataclass
        class __frames__:
            console: tk.Frame
            entry: tk.Entry
        
        @dataclass
        class __vars__:
            console: tk.StringVar = field(default_factory=tk.StringVar)
            entry: tk.StringVar = field(default_factory=tk.StringVar)
            fetch: Queue = field(default_factory=Queue)

        @dataclass
        class __threads__:
            stdout: Thread
        
        cls.frames = __frames__
        cls.vars = __vars__
        cls.threads = __threads__

        return super().__new__(cls)

    def __init__(self):

        self.root = tk.Tk(className='control panel')
        self.vars = self.vars()
        self.threads = self.threads(
            stdout = Thread(target=self.console_update, name='toolbox.interface.stdout', daemon=True)
        )

        self.threads.stdout.start()

        self.root.title('Tello Drone Control Panel')
        self.root.iconbitmap(path.icon)
        self.root.geometry(Gadget.getGeometry(window=self.root))
        self.root.option_add('*font', ('Consolas', 12, 'normal'))

        self.__init_buildtree__()


    def __init_buildtree__(self):
        self.frames = self.frames(
            console = tk.Label(self.root, fg=color.white, bg=color.black, justify=tk.LEFT, anchor=tk.NW, textvariable=self.vars.console),
            entry = tk.Entry(self.root, fg=color.white, bg=color.black, justify=tk.LEFT, textvariable=self.vars.entry, bd=4, relief=tk.RIDGE)
        )

        return self.__init_position__()

    def __init_position__(self):
        self.frames.console.grid(sticky=tk.NSEW)
        self.frames.entry.grid(sticky=tk.NSEW, ipady=4)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        return self.__init_behaviour__()
    
    def __init_behaviour__(self):
        self.frames.entry.bind('<Return>', lambda _: self.console_input(self.vars.entry.get()))
        #self.root.bind_all('<Key>', self.console_update)
        #console.info('Bind!')

        return self.__init_adjustment__()
    
    def __init_adjustment__(self):
        return self
    
    def console_update(self):
        while True:
            sleep(.1)
            self.vars.console.set(logs.getvalue())


    def console_input(self, *string: str, sep: str = ' ', end: str = '\n'):
        fetch = sep.join(map(str, string))
        sys.stdout.write(fetch + end)
        self.vars.fetch.put_nowait(fetch)
        self.vars.entry.set('')

        #console.info(fetch)

        return fetch

class interface:

    def __init__(self) -> None:
        ...
    


def input(prompt: str = ''):
        if window is None: return
        sys.stdout.write(prompt)
        return window.vars.fetch.get()
        #window.console_input()

window = _ = ControlPanel()
_.root.mainloop()

sys.stdout = sys.__stdout__
print(logs.getvalue())
