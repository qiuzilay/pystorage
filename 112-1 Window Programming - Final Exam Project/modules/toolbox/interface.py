from os import chdir, getcwd, pardir, sep
from os.path import dirname, realpath, join
from importlib import import_module, reload
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Self, Any
from threading import Thread
from queue import Queue
from io import StringIO
#from multiprocessing import Process
import subprocess
import tkinter.ttk as ttk
import tkinter as tk
import time
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

class DynamicScrollbar(ttk.Scrollbar):

    def __init__(self, master, orient: Literal['vertical', 'horizontal'], *args, **kwargs):
        super().__init__(master=master, orient=orient, *args, **kwargs)
        self.master: tk.Frame
        self.orient = orient
        self.display = True

    def set(self, first: float | str, last: float | str):
        if float(first) == 0.0 and float(last) == 1.0:
            if self.display:
                self.place_forget()
                self.display = False
        else:
            if not self.display:
                match self.orient:
                    case 'vertical':
                        self.place(relx=1, rely=0, relheight=1, anchor=tk.NE)
                    case 'horizontal':
                        self.place(relx=0, rely=1, relwidth=1, anchor=tk.SW)
                self.display = True

        super().set(first, last)

class StdoutRework(StringIO):
    def __init__(self, widget: tk.Text, *args) -> None:
        super().__init__(*args)
        self.text = widget
    
    def write(self, __s: str) -> int:
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, __s)
        self.text.config(state=tk.DISABLED)
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

    @property
    def defaultFont(self):
        return ('Consolas', self.states.font_size, 'normal')

    def __new__(cls, *args, **kwargs) -> Self:

        @dataclass
        class __frames__:
            console: tk.Frame = None
            entry: tk.Frame = None
            entry_inner: tk.Frame = None
        
        @dataclass
        class __units__:
            console: tk.Text = None
            entry_input: tk.Entry = None
            entry_prompt: tk.Label = None
            vscrollbar: ttk.Scrollbar = None
            hscrollbar: ttk.Scrollbar = None
        
        @dataclass
        class __vars__:
            #console: tk.StringVar = field(default_factory=tk.StringVar)
            entry: tk.StringVar = field(default_factory=tk.StringVar)
            prompt: tk.StringVar = field(default_factory=tk.StringVar)

        @dataclass
        class __states__:
            listening: bool = False
            font_size: int = 12
        
        cls.frames = __frames__
        cls.units = __units__
        cls.vars = __vars__
        cls.states = __states__()
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
                self.root.option_add('*font', self.defaultFont)
        
        self.vars = self.vars()
        self.style = ttk.Style(self.root)
        self.style.theme_use('alt')
        self.style.layout(
            'arrowless.Vertical.TScrollbar', 
            [(
                'Vertical.Scrollbar.trough', {
                    'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': tk.NSEW})],
                    'sticky': tk.NS
                }
            )]
        )
        self.style.layout(
            'arrowless.Horizontal.TScrollbar', 
            [(
                'Horizontal.Scrollbar.trough', {
                    'children': [('Horizontal.Scrollbar.thumb', {'expand': '1', 'sticky': tk.NSEW})],
                    'sticky': tk.EW
                }
            )]
        )
        self.style.configure('arrowless.Vertical.TScrollbar', troughcolor='black')
        self.style.configure('arrowless.Horizontal.TScrollbar', troughcolor='black')

        self.__init_buildtree__()

    def __init_buildtree__(self) -> Self:
        
        self.frames = self.frames(
            console = tk.Frame(self.root, bg=color.black, bd=0, highlightthickness=0),
            entry = tk.Frame(self.root, bg=color.black, bd=0, highlightthickness=0)
        )
        
        self.frames.entry_inner = tk.Text(self.frames.entry, fg=color.white, bg=color.black, state=tk.DISABLED)

        self.units = self.units(
            console = tk.Text(self.frames.console, fg=color.white, bg=color.black, wrap=tk.NONE, state=tk.DISABLED),
            entry_input = tk.Entry(self.frames.entry_inner, fg=color.white, bg=color.black, justify=tk.LEFT, textvariable=self.vars.entry, bd=0, highlightthickness=0),
            entry_prompt = tk.Label(self.frames.entry_inner, fg=color.white, bg=color.black, textvariable=self.vars.prompt, bd=0, highlightthickness=0)
        )
        
        self.units.vscrollbar = DynamicScrollbar(self.units.console, orient='vertical', style='arrowless.Vertical.TScrollbar')
        self.units.hscrollbar = DynamicScrollbar(self.units.console, orient='horizontal', style='arrowless.Horizontal.TScrollbar')

        return self.__init_position__()

    def __init_position__(self) -> Self:

        self.frames.console.grid(sticky=tk.NSEW)
        self.frames.entry.grid(sticky=tk.NSEW)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.units.console.grid(padx=8, pady=(8, 4), sticky=tk.NSEW)
        self.frames.console.grid_rowconfigure(0, weight=1)
        self.frames.console.grid_columnconfigure(0, weight=1)
        
        self.frames.entry_inner.grid(padx=8, pady=(4, 8), ipadx=4, ipady=8, sticky=tk.NSEW)
        self.frames.entry.grid_rowconfigure(0, weight=1)
        self.frames.entry.grid_columnconfigure(0, weight=1)

        self.units.entry_prompt.grid(row=0, column=0, padx=(4, 0), sticky=tk.NSEW)
        self.units.entry_input.grid(row=0, column=1, padx=(0, 4), sticky=tk.NSEW)
        self.frames.entry_inner.grid_rowconfigure(0, weight=1)
        self.frames.entry_inner.grid_columnconfigure(1, weight=1)
        
        self.units.vscrollbar.place(relx=1, rely=0, relheight=1, anchor=tk.NE)
        self.units.hscrollbar.place(relx=0, rely=1, relwidth=1, anchor=tk.SW)

        self.root.update_idletasks()

        return self.__init_behaviour__()
    
    def __init_behaviour__(self) -> Self:
        self.units.entry_input.bind('<Return>', lambda _: self.console_input(self.vars.entry.get()))
        self.units.console.bind('<Control-MouseWheel>', self.zoom)

        return self.__init_adjustment__()
    
    def __init_adjustment__(self) -> Self:

        self.queue = Queue()
        self.logs = StdoutRework(widget=self.units.console)
        
        self.units.vscrollbar.config(command=self.units.console.yview)
        self.units.hscrollbar.config(command=self.units.console.xview)
        self.units.console.config(yscrollcommand=self.units.vscrollbar.set, xscrollcommand=self.units.hscrollbar.set)

        return self
    
    def console_input(self, *string: str, sep: str = ' ', end: str = '\n') -> str:

        string: str = sep.join(map(str, string)).strip('\n')
        prefix: str = f'[{datetime.now().strftime("%H:%M:%S")}] '

        if self.states.listening:
            if not self.logs.getvalue().endswith('\n') or string:
                sys.stdout.write(prefix + self.vars.prompt.get() + string + end)
            self.queue.put_nowait(string)
        else:
            match string:
                case _ if string.strip('()').startswith(('exit', 'stop', 'end')):
                    self.window.root.destroy()
                case _:
                    subproc = subprocess.Popen(string, shell=True, text=True, cwd=getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
                    for line in iter(subproc.stdout.readline, ''):
                        sys.stdout.write('>>> ' + str(line.rstrip()) + '\n')
                        sys.stdout.flush()
        self.vars.entry.set('')
        return string
    
    def zoom(self, event: tk.Event) -> None:
        
        self.prompt: tk.Frame | None
        
        def implement():
            nonlocal self, event
            self.states.font_size += int(event.delta / 120)
            self.units.console.config(font=self.defaultFont)
                
            self.prompt = tk.Frame(self.root, bg=color.black, border=0, highlightthickness=0)
            prompt_inner = tk.Label(
                self.prompt,
                text = f'x{apchInt(Gadget.round(self.states.font_size/12))}',
                font = self.defaultFont,
                fg = color.white,
                bg = color.black,
                border = 0,
                highlightthickness = 1
            )
            prompt_inner.pack(ipadx=8, pady=4, fill=tk.BOTH)
            self.prompt.place(relx=0.95, rely=0.05, anchor=tk.NE)
            self.prompt.after(1500, self.prompt.destroy)
            
        try:
            assert (event.delta > 0) or (self.states.font_size > 10) # @IgnoreException
            self.prompt.destroy() # @IgnoreException
            del self.prompt
            
        except AssertionError: ...
        except AttributeError: implement()        
        else: implement()     