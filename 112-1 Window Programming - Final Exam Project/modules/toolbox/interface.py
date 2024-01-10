from os import chdir, getcwd, pardir, sep
from os.path import dirname, realpath, join
from importlib import import_module, reload
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self, Any
from threading import Thread
from queue import Queue
from time import sleep
from io import StringIO
#from multiprocessing import Process
import subprocess
import tkinter.ttk as ttk
import tkinter as tk
import sys

chdir(dirname(realpath(__file__))) if __name__.__eq__('__main__') else ...

dirpath = realpath(join(__file__, pardir)).removeprefix(getcwd()).lstrip(sep)
modpath = dirpath.replace(sep, ".")

try:
    from __init__ import array, slider, String, Enum, Console, cmdl, Gadget, json, is_number, is_integer, apchInt, console # @IgnoreException
except ImportError:
    dirpath = realpath(join(__file__, pardir)).removeprefix(getcwd()).lstrip(sep)
    toolbox = import_module(modpath)
    array = toolbox.array
    slider = toolbox.slider
    String = toolbox.String
    Enum = toolbox.Enum
    cmdl = toolbox.cmdl
    Gadget = toolbox.Gadget
    json = toolbox.json
    is_number = toolbox.is_number
    is_integer = toolbox.is_integer
    apchInt = toolbox.apchInt
    console = toolbox.console

@dataclass
class path:
    icon: str

path = path(
    icon = join(dirpath, 'images', 'icon.ico')
)

class color(Enum):
    white = '#FFFFFF'
    black = '#000000'

class StdoutRework(StringIO):
    def __init__(self, widget: tk.Text, *args) -> None:
        super().__init__(*args)
        self.text = widget
    
    def write(self, __s: str) -> int:
        self.text.insert(tk.END, __s)
        return super().write(__s)

def input(prompt: str = '') -> Any:
    if sys.stdout is sys.__stdout__: raise RuntimeError('you have to create a terminal first before using this function.')
    terminal.window.states.listening = True
    terminal.window.queue.queue.clear()
    terminal.window.vars.prompt.set(prompt)
    terminal.window.units.entry_prompt.grid()
    fetch = terminal.window.queue.get() # blocker
    terminal.window.vars.prompt.set('')
    terminal.window.states.listening = False
    return fetch

class terminal:

    @classmethod
    def create(cls, root: tk.Tk | tk.Widget = None, daemon: bool = False) -> tk.Tk | tk.Toplevel | tk.Frame:
        try:
            cls.window.root # @IgnoreException
            
        except AttributeError:
            
            if not root:
                thread = Thread(
                    target = cls.__async__,
                    name = f'{modpath}.interface.terminal' if modpath else 'interface.terminal',
                    daemon = daemon
                )
                thread.start()
                while sys.stdout is sys.__stdout__: ...
                
            else:
                cls.__sync__(root)
                
        
        else:
            raise RuntimeError('only one terminal existing is allowed.') # @IgnoreException
        
        finally:
            return cls.window.root

    @classmethod
    def __sync__(cls, root: tk.Tk | tk.Widget | None) -> None:
        terminal(root)
        sys.stdout = cls.window.logs

    @classmethod
    def __async__(cls) -> None:
        window = terminal()
        sys.stdout = cls.window.logs
        window.root.mainloop()
        sys.stdout = sys.__stdout__
        sys.stdout.write(window.logs.getvalue())

    def __new__(cls, *args, **kwargs) -> Self:

        @dataclass
        class __frames__:
            console: tk.Frame
            entry: tk.Frame
        
        @dataclass
        class __units__:
            console: tk.Text
            entry_input: tk.Entry
            entry_prompt: tk.Label
        
        @dataclass
        class __vars__:
            #console: tk.StringVar = field(default_factory=tk.StringVar)
            entry: tk.StringVar = field(default_factory=tk.StringVar)
            prompt: tk.StringVar = field(default_factory=tk.StringVar)

        @dataclass
        class __states__:
            listening: bool = False
        
        cls.frames = __frames__
        cls.units = __units__
        cls.vars = __vars__
        cls.states = __states__
        cls.window = super().__new__(cls)

        return cls.window

    def __init__(self, root: tk.Tk | tk.Widget | None = None) -> None:
        match root:
            case _ if isinstance(root, tk.Tk):
                self.root = tk.Toplevel(root)
            case _ if isinstance(root, tk.Widget):
                self.root = tk.Frame(root)
            case _:
                self.root = tk.Tk(className='terminal')
                self.root.title('Terminal')
                self.root.iconbitmap(path.icon)
                self.root.geometry(Gadget.getGeometry(window=self.root))
                self.root.option_add('*font', ('Consolas', 10, 'normal'))
        
        self.states = self.states()
        self.vars = self.vars()

        self.__init_buildtree__()

    def __init_buildtree__(self) -> Self:
        
        self.frames = self.frames(
            console = tk.Frame(self.root, bg=color.black, bd=0, highlightthickness=0),
            entry = tk.Frame(self.root, bg=color.black, bd=8, highlightthickness=0, relief=tk.SUNKEN)
        )

        self.units = self.units(
            console = tk.Text(self.frames.console, fg=color.white, bg=color.black),
            entry_input = tk.Entry(self.frames.entry, fg=color.white, bg=color.black, justify=tk.LEFT, textvariable=self.vars.entry, bd=0, highlightthickness=0),
            entry_prompt = tk.Label(self.frames.entry, fg=color.white, bg=color.black, textvariable=self.vars.prompt, bd=0, highlightthickness=0)
        )

        return self.__init_position__()

    def __init_position__(self) -> Self:

        self.frames.console.grid(sticky=tk.NSEW)
        self.frames.entry.grid(sticky=tk.NSEW)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.units.console.grid(sticky=tk.NSEW, padx=8, pady=8)
        self.frames.console.grid_rowconfigure(0, weight=1)
        self.frames.console.grid_columnconfigure(0, weight=1)

        self.units.entry_prompt.grid(row=0, column=0, sticky=tk.NSEW, padx=(4, 0))
        self.units.entry_input.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 4))
        self.frames.entry.grid_columnconfigure(1, weight=1)

        self.root.update_idletasks()

        return self.__init_behaviour__()
    
    def __init_behaviour__(self) -> Self:
        self.units.entry_input.bind('<Return>', lambda _: self.console_input(self.vars.entry.get()))

        return self.__init_adjustment__()
    
    def __init_adjustment__(self) -> Self:

        self.queue = Queue()
        self.logs = StdoutRework(widget=self.units.console)

        return self
    
    def console_input(self, *string: str, sep: str = ' ', end: str = '\n') -> str:

        string = sep.join(map(str, string)).strip('\n')
        prefix = f'[{datetime.now().strftime("%H:%M:%S")}] '

        if self.states.listening:
            if not self.logs.getvalue().endswith('\n') or string:
                print(prefix + self.vars.prompt.get() + string, end=end)
            self.queue.put_nowait(string)
        else:
            subproc = subprocess.Popen(string, shell=True, text=True, cwd=getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
            for line in iter(subproc.stdout.readline, ''):
                print('>>> ' + str(line.rstrip()))
        self.vars.entry.set('')
        return string