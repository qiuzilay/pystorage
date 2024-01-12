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
    timestamp: str

path = path(
    icon = join(dirpath, 'images', 'icon.ico'),
    timestamp = join(dirpath, 'images', 'timestamp.png')
)

class color(Enum):
    white = '#FFFFFF'
    lightgray = '#D3D3D3'
    gray = '#808080'
    dimgray = '#696969'
    black = '#000000'

class DynamicScrollbar(ttk.Scrollbar):

    def __init__(self, master, orient: Literal['vertical', 'horizontal'], owner: tk.Text = ..., partner: tk.Text = ..., *args, **kwargs):
        super().__init__(master=master, orient=orient, *args, **kwargs)
        self.master: tk.Frame
        self.orient = orient
        self.owner = owner
        self.partner = partner
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
        
        
        self.partner.yview_moveto(self.owner.yview()[0]) if Ellipsis not in (self.owner, self.partner) else ...
        super().set(first, last)

class StdoutRework(StringIO):
    def __init__(self, widget: tk.Text, timestamp: tk.Text, *args) -> None:
        super().__init__(*args)
        self.widget = widget
        self.timestamp = timestamp
    
    def write(self, __s: str) -> int:
        prefix = f'[{datetime.now().strftime("%H:%M:%S")}]'
        
        yview = self.widget.yview()[1]
        
        self.widget.config(state=tk.NORMAL)
        self.timestamp.config(state=tk.NORMAL)
        
        self.widget.insert(tk.END, __s)
        self.timestamp.insert(tk.END, prefix + '\n' * __s.count('\n')) if __s.endswith('\n') else ...
        
        self.timestamp.config(state=tk.DISABLED)
        self.widget.config(state=tk.DISABLED)
        
        self.widget.yview_moveto(1) if yview > .975 else ...
        self.timestamp.yview_moveto(1) if yview > .975 else ...
        
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

    @staticmethod
    def create_rounded_rectangle(canvas: tk.Canvas ,x1: int, y1: int, x2: int, y2: int, radius: int, **kwargs):
        return canvas.create_polygon([
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ], **kwargs, smooth = True)

    @property
    def defaultFont(self):
        return ('Consolas', self.states.font_size, 'normal')

    def __new__(cls, *args, **kwargs) -> Self:

        @dataclass
        class __frames__:
            console: tk.Frame = None
            entry: tk.Frame = None
            entry_inner: tk.Frame = None
            timestamp: tk.Frame = None
        
        @dataclass
        class __units__:
            console: tk.Text = None
            timestamp: tk.Text = None
            entry_input: tk.Entry = None
            entry_prompt: tk.Label = None
            vscrollbar: ttk.Scrollbar = None
            hscrollbar: ttk.Scrollbar = None
            toggle_ts: tk.Canvas = None
        
        @dataclass
        class __vars__:
            #console: tk.StringVar = field(default_factory=tk.StringVar)
            entry: tk.StringVar = field(default_factory=tk.StringVar)
            prompt: tk.StringVar = field(default_factory=tk.StringVar)

        @dataclass
        class __states__:
            listening: bool = False
            font_size: int = 12
            tsframe: bool = False
        
        @dataclass
        class __images__:
            toggle_ts: tk.PhotoImage
            
        @dataclass
        class __configID__:
            image_toggle_ts: int = None
            polygon_toggle_ts: int = None
        
        cls.frames = __frames__
        cls.units = __units__
        cls.vars = __vars__
        cls.images = __images__
        cls.states = __states__()
        cls.configID = __configID__()
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
        self.images = self.images(toggle_ts=tk.PhotoImage(file=path.timestamp).subsample(8))
        self.style = ttk.Style(self.root)
        
        for orient in ('Vertical', 'Horizontal'):
            self.style.element_create(f'arrowless.{orient}.Scrollbar.trough', 'from', 'alt')
            self.style.element_create(f'arrowless.{orient}.Scrollbar.thumb', 'from', 'alt')
            self.style.element_create(f'arrowless.{orient}.Scrollbar.grip', 'from', 'alt')
            self.style.layout(
                f'arrowless.{orient}.Scrollbar',
                [(
                    f'arrowless.{orient}.Scrollbar.trough', {
                        'children': [(
                            f'arrowless.{orient}.Scrollbar.thumb', {
                                'unit': '1',
                                'children': [(f'arrowless.{orient}.Scrollbar.grip', {'sticky': ''})],
                                'sticky': tk.NSEW
                            }
                        )],
                        'sticky': tk.NS if orient.__eq__('Vertical') else tk.EW if orient.__eq__('Horizontal') else tk.NSEW
                    }
                )]
            )
            self.style.configure(f'arrowless.{orient}.Scrollbar', troughcolor='black')

        self.__init_buildtree__()

    def __init_buildtree__(self) -> Self:
        
        self.frames = self.frames(
            console = tk.Frame(self.root, bg=color.black, bd=0, highlightthickness=0),
            entry = tk.Frame(self.root, bg=color.black, bd=0, highlightthickness=0),
            timestamp = tk.Frame(self.root, bg=color.black, bd=0, highlightthickness=0)
        )
        
        self.frames.entry_inner = tk.Text(self.frames.entry, fg=color.white, bg=color.black, bd=4, state=tk.DISABLED)

        self.units = self.units(
            console = tk.Text(self.frames.console, fg=color.white, bg=color.black, wrap=tk.NONE, bd=4, state=tk.DISABLED, cursor='arrow'),
            entry_input = tk.Entry(self.frames.entry_inner, fg=color.white, bg=color.black, justify=tk.LEFT, textvariable=self.vars.entry, bd=0, highlightthickness=0),
            entry_prompt = tk.Label(self.frames.entry_inner, fg=color.white, bg=color.black, textvariable=self.vars.prompt, bd=0, highlightthickness=0),
            timestamp = tk.Text(self.frames.timestamp, width=10, fg=color.white, bg=color.black, wrap=tk.NONE, bd=4, state=tk.DISABLED, cursor='arrow')
        )
        
        self.units.toggle_ts = tk.Canvas(self.frames.timestamp, bg=color.black, bd=0, highlightthickness=0, width=Gadget.scaler(56), height=Gadget.scaler(56), cursor='arrow')
        self.units.vscrollbar = DynamicScrollbar(self.units.console, owner=self.units.console, partner=self.units.timestamp, orient='vertical', style='arrowless.Vertical.Scrollbar')
        self.units.hscrollbar = DynamicScrollbar(self.units.console, orient='horizontal', style='arrowless.Horizontal.Scrollbar')

        return self.__init_position__()

    def __init_position__(self) -> Self:

        self.frames.timestamp.grid(row=0, column=0, sticky=tk.NS)
        self.frames.console.grid(row=0, column=1, sticky=tk.NSEW)
        self.frames.entry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.units.console.grid(padx=(0, 8), pady=(8, 4), sticky=tk.NSEW)
        self.frames.console.grid_rowconfigure(0, weight=1)
        self.frames.console.grid_columnconfigure(0, weight=1)
        
        self.units.timestamp.grid(row=0, column=0, padx=(8, 0), pady=(8, 4), sticky=tk.NSEW)
        self.units.toggle_ts.grid(row=0, column=0, padx=8, pady=8, sticky=tk.N)
        self.frames.timestamp.grid_rowconfigure(0, weight=1)
        self.frames.timestamp.grid_columnconfigure(0, weight=1)
        
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
        self.units.toggle_ts.bind('<Button-1>', self.timestamp)
        self.units.timestamp.bind('<Button-1>', self.timestamp)

        return self.__init_adjustment__()
    
    def __init_adjustment__(self) -> Self:

        self.queue = Queue()
        self.logs = StdoutRework(widget=self.units.console, timestamp=self.units.timestamp)
        
        def yview_bundle(*args, **kwargs):
            self.units.console.yview(*args, **kwargs)
            self.units.timestamp.yview(*args, **kwargs)
        
        self.units.vscrollbar.config(command=yview_bundle)
        self.units.hscrollbar.config(command=self.units.console.xview)
        self.units.console.config(yscrollcommand=self.units.vscrollbar.set, xscrollcommand=self.units.hscrollbar.set)
        self.units.timestamp.config(yscrollcommand=self.units.vscrollbar.set)
        
        self.units.timestamp.grid_remove()
        
        self.configID.polygon_toggle_ts = self.create_rounded_rectangle(
            self.units.toggle_ts,
            2, 2, 
            self.units.toggle_ts.winfo_width()-2, self.units.toggle_ts.winfo_height()-2,
            radius = 4,
            outline = color.dimgray,
            fill = color.black
        )
        
        self.configID.image_toggle_ts = self.units.toggle_ts.create_image(
            self.units.toggle_ts.winfo_width()/2,
            self.units.toggle_ts.winfo_height()/2,
            image = self.images.toggle_ts
        )

        return self
    
    def console_input(self, *string: str, sep: str = ' ', end: str = '\n') -> str:

        string: str = sep.join(map(str, string)).strip('\n')

        if self.states.listening:
            if not self.logs.getvalue().endswith('\n') or string:
                sys.stdout.write(self.vars.prompt.get() + string + end)
            self.queue.put_nowait(string)
        else:
            match string:
                case _ if string.strip('()').startswith(('exit', 'stop', 'end')):
                    self.window.root.destroy()
                case _:
                    subproc = subprocess.Popen(string, shell=True, text=True, cwd=getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
                    sys.stdout.write(f'{realpath(getcwd())}> ' + string + '\n')
                    stdout, _ = subproc.communicate()
                    sys.stdout.write(stdout + '\n')
                    sys.stdout.flush()
                    # for line in iter(subproc.stdout.readline, ''):
                    #     sys.stdout.write('>>> ' + str(line.rstrip()) + '\n')
                    #     sys.stdout.flush()
        self.vars.entry.set('')
        return string
    
    def zoom(self, event: tk.Event) -> None:
        
        self.prompt: tk.Frame | None
        
        def implement():
            nonlocal self, event
            self.states.font_size += int(event.delta / 120)
            self.units.console.config(font=self.defaultFont)
            self.units.timestamp.config(font=self.defaultFont)
                
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

    def timestamp(self, event: tk.Event) -> None:
        
        # expand -> collapse
        if self.states.tsframe:
            self.units.timestamp.grid_remove()
            self.units.toggle_ts.grid()
            self.states.tsframe = False
            
        # collapse -> expand
        else:
            self.units.toggle_ts.grid_remove()
            self.units.timestamp.grid()
            self.states.tsframe = True