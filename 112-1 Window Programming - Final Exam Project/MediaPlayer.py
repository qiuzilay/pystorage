from __future__ import annotations
from os import chdir, getcwd
from os.path import dirname, realpath, basename

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

from modules.toolbox import Gadget, Enum, array, console
from dataclasses import dataclass, field
from functools import partial
from typing import Literal
from threading import Thread
from time import sleep
from random import sample
from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as filedialog
import pygame  # 引入Pygame模組，用於音樂播放

class eventID(Enum):
    music_end = 19132

class color(Enum):
    white = '#FFFFFF'
    deepblue = '#006699'
    lightgray = '#D3D3D3'
    dimgray = '#696969'
    darkgray = '#404040'
    black = '#000000'
    transparent = '#010101'

class font(Enum):
    default = ('Microsoft JhengHei', 10, 'normal')
    bold = ('Microsoft JhengHei', 10, 'bold')

class DynamicScrollbar(ttk.Scrollbar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent: tk.Frame = self.master
        self.display = True

    def set(self, first: float | str, last: float | str):
        if float(first) == 0.0 and float(last) == 1.0:
            if self.display:
                self.grid_remove()
                self.parent.grid(padx = (16, 16))
                self.display = False
        else:
            if not self.display:
                self.parent.grid(padx = (16, 0))
                self.grid()
                self.display = True

        super().set(first, last)

class AudioFile:
    
    def __init__(self, root: MusicPlayer, parent: tk.Tk | tk.Frame, path: str):
        
        self.root = root
        self.id = self.root.states.serial
        self.root.states.serial += 1
        self.selected = tk.BooleanVar()
        self.frame = tk.Frame(parent, name=f'playlist-audio_{self.id}', bg=color.white)
        self.frame.hover = False

        @dataclass
        class metadata:
            name: str
            path: str
            length: float

        self.data = metadata(
            name = basename(path),
            path = realpath(path),
            length = Gadget.round(pygame.mixer.Sound(path).get_length(), format='0')
        )

        @dataclass
        class labels:
            name = tk.Label(self.frame, text=self.data.name, anchor=tk.W, width=40)
            length = tk.Label(self.frame, text=Gadget.timeformat(self.data.length), anchor=tk.W, width=10)

        self.labels = labels()
        self.labels.name.grid(row=0, column=0, padx=(1, 0.5), pady=1, sticky=tk.NSEW)
        self.labels.length.grid(row=0, column=1, padx=(0.5, 1), pady=1, sticky=tk.NSEW)
        
        self.frame.columnconfigure(0, weight=4)
        self.frame.columnconfigure(1, weight=1)

        self.selected.trace_add('write', self.event_selected)
        self.frame.bind('<Enter>', root.hover_on)
        self.frame.bind('<Leave>', root.hover_off)
        self.frame.bind('<Double-Button-1>', self.trigger)
        self.labels.name.bind('<Double-Button-1>', self.trigger)
        self.labels.length.bind('<Double-Button-1>', self.trigger)

    def trigger(self, event=..., cause_pointer_moved=False):
        match (self.selected.get(), bool(self.root.states.selected)):
            case (True, True):
                self.selected.set(False)
                self.root.states.selected = None
            case (True, False):
                raise Exception('An impossible situation occurred.')
            case (False, True):
                self.root.states.selected.selected.set(False)
                self.selected.set(True)
                self.root.states.selected = self
                if cause_pointer_moved: return
                for index, file in enumerate(self.root.queue):
                    if id(file) == id(self):
                        self.root.states.pointer.set(index)
                        self.root.play_music(status='stop')
                        break

            case (False, False):
                self.selected.set(True)
                self.root.states.selected = self
                if cause_pointer_moved: return
                for index, file in enumerate(self.root.queue):
                    if id(file) == id(self):
                        self.root.states.pointer.set(index)
                        self.root.play_music(status='stop')
                        break

    def event_selected(self, *args, **kwargs):
        match (self.selected.get(), self.frame.hover):
            case (True, True):
                self.frame.config(bg=color.darkgray)
                self.labels.name.config(bg=color.darkgray, fg=color.white, font=font.bold)
                self.labels.length.config(bg=color.darkgray, fg=color.white, font=font.bold)
                self.root.states.hover.child.fgcolor = color.deepblue
                self.root.states.hover.child.font = font.bold
            case (True, False):
                self.labels.name.config(fg=color.deepblue, font=font.bold)
                self.labels.length.config(fg=color.deepblue, font=font.bold)
            case (False, True):
                self.labels.name.config(fg=color.white, font=font.default)
                self.labels.length.config(fg=color.white, font=font.default)
                self.root.states.hover.child.fgcolor = color.black
                self.root.states.hover.child.font = font.default
            case (False, False):
                self.labels.name.config(fg=color.black, font=font.default)
                self.labels.length.config(fg=color.black, font=font.default)
        
class MusicPlayer:

    def __new__(cls, *args, **kwargs):

        @dataclass
        class __frames__: # frameworks
            menu: tk.Menu = None
            menu_file: tk.Menu = None # child of frames.menu
            playlist: tk.Frame = None
            playlist_label: tk.Frame = None
            playlist_canvas: tk.Canvas = None
            playlist_frame: tk.Frame = None
            progress: tk.Frame = None
            basic: tk.Frame = None
            basic_volume: tk.Frame = None # child of frames.basic

        @dataclass
        class __units__:
            button_play: tk.Canvas
            button_stop: tk.Canvas
            button_prev: tk.Canvas
            button_next: tk.Canvas
            button_repeat: tk.Canvas
            button_shuffle: tk.Canvas
            button_volume: tk.Canvas
            optbar_volume: ttk.Scale
            optbar_progress: ttk.Scale
            label_progress: tk.Label
            scroll_bar: DynamicScrollbar

        @dataclass
        class __images__:
            button_play: tk.PhotoImage = tk.PhotoImage(file='./images/button_play 128x.png').subsample(2)
            button_pause: tk.PhotoImage = tk.PhotoImage(file='./images/button_pause 128x.png').subsample(2)
            button_prev: tk.PhotoImage = tk.PhotoImage(file='./images/button_previous 128x.png').subsample(3)
            button_next: tk.PhotoImage = tk.PhotoImage(file='./images/button_next 128x.png').subsample(3)
            button_stop: tk.PhotoImage = tk.PhotoImage(file='./images/button_stop 128x.png').subsample(4)
            button_repeat: tuple[tk.PhotoImage, ...] = (
                tk.PhotoImage(file='./images/button_repeat.png').subsample(4),
                tk.PhotoImage(file='./images/button_repeat_glow.png').subsample(4),
                tk.PhotoImage(file='./images/button_repeat_hyperglow.png').subsample(4),
            )
            button_shuffle: tuple[tk.PhotoImage, ...] = (
                tk.PhotoImage(file='./images/button_shuffle.png').subsample(4),
                tk.PhotoImage(file='./images/button_shuffle_glow.png').subsample(4)
            )
            button_volume: tuple[tk.PhotoImage, ...] = (
                tk.PhotoImage(file='./images/volume_0.png').subsample(4),
                tk.PhotoImage(file='./images/volume_1.png').subsample(4),
                tk.PhotoImage(file='./images/volume_2.png').subsample(4)
            )

        @dataclass
        class __hover__:
            widget: tk.Widget = None
            fgcolor: object = None
            bgcolor: object = None
            font: object = None
            child: __hover__ = None

        @dataclass
        class __monitor__:
            event_handler: Thread
            progress_bar: Thread

        @dataclass
        class __states__:
            status: Literal['playing', 'pause', 'stop'] = 'stop'
            serial: int = 0
            diff: float = 0
            selected: AudioFile = None
            hover: __hover__ = None
            isdragging: bool = False
            repeat: Literal[0, 1, 2] = 0
            random: bool = False
            pointer: tk.IntVar = field(default_factory=tk.IntVar)
            volume: tk.IntVar = field(default_factory=tk.IntVar)
            progress_pct: tk.DoubleVar = field(default_factory=tk.DoubleVar)
            playlist_label_width: int = None

        @dataclass
        class __cfgIDs__:
            button_play: int = None
            button_stop: int = None
            button_prev: int = None
            button_next: int = None
            button_shuffle: int = None
            button_repeat: int = None
            button_volume: int = None
            playlist_frame: int = None

        cls.frames = __frames__
        cls.units = __units__
        cls.images = __images__
        cls.hover = __hover__
        cls.monitor = __monitor__
        cls.states = __states__
        cls.cfgIDs = __cfgIDs__

        return super().__new__(cls)

    def __init__(self, window:tk.Tk):
            
        btnsize = Gadget.scaler(80)
        
        self.window = window
        self.volume = 100
        self.queue = array()
        self.cfgIDs = self.cfgIDs()
        self.states = self.states()
        self.images = self.images()
        self.frames = self.frames(
            menu = tk.Menu(window),
            playlist = tk.Frame(window),
            progress = tk.Frame(window),
            basic = tk.Frame(window)
        )
        self.frames.menu_file = tk.Menu(self.frames.menu, tearoff=False)
        self.frames.playlist_label = tk.Frame(self.frames.playlist, bg=color.white)
        self.frames.playlist_canvas = tk.Canvas(self.frames.playlist, bg=color.white, bd=0, highlightthickness=0)
        self.frames.playlist_frame = tk.Frame(self.frames.playlist_canvas, bg=color.white)
        self.frames.basic_volume = tk.Frame(self.frames.basic)
        self.units = self.units(
            button_play = tk.Canvas(self.frames.basic, width=int(btnsize), height=int(btnsize)),
            button_prev = tk.Canvas(self.frames.basic, width=int(btnsize*0.75), height=int(btnsize*0.75)),
            button_next = tk.Canvas(self.frames.basic, width=int(btnsize*0.75), height=int(btnsize*0.75)),
            button_stop = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_repeat = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_shuffle = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_volume = tk.Canvas(self.frames.basic_volume, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            optbar_volume = ttk.Scale(self.frames.basic_volume, from_=0, to=100, variable=self.states.volume, length=int(btnsize), command=self.adjust_volume),
            optbar_progress = ttk.Scale(self.frames.progress, from_=0, to=100, variable=self.states.progress_pct),
            label_progress = tk.Label(self.frames.progress, text='00:00'),
            scroll_bar = DynamicScrollbar(self.frames.playlist, command=self.frames.playlist_canvas.yview, style='arrowless.Vertical.TScrollbar')
        )

        minsize = Gadget.getGeometry(window, width=360, height=480, output='metadata')
        
        style = ttk.Style(self.window)
        style.theme_use('vista')
        style.layout(
            'arrowless.Vertical.TScrollbar', 
            [(
                'Vertical.Scrollbar.trough', {
                    'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': tk.NSEW})],
                    'sticky': tk.NS
                }
            )]
        )
        style.configure("arrowless.Vertical.TScrollbar", background="green", bordercolor="red")
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume/100)
        pygame.mixer.music.set_endevent(eventID.music_end)
        self.states.volume.set(self.volume)
        self.states.pointer.set(-1)
        self.window.title('Simple Music Player')
        self.window.iconbitmap('mediaplayer.ico')
        self.window.geometry(Gadget.getGeometry(window, width=540, height=720))
        self.window.minsize(width=minsize.width, height=minsize.height)
        self.window.config(menu=self.frames.menu)
        self.window.option_add('*font', font.default)
        self.window.wm_attributes('-transparentcolor', color.transparent)

        self.frames.menu_file.add_command(label='Import', command=self.add_song)
        self.frames.menu.add_cascade(label='File', menu=self.frames.menu_file)
                
        self.__init_position__()\
            .__init_appearance__()\
            .__init_behavior__()
        
        self.frames.playlist_canvas.config(yscrollcommand=self.units.scroll_bar.set, scrollregion=self.frames.playlist_canvas.bbox(tk.ALL))
        
        self.monitor = self.monitor(
            event_handler = Thread(target=self.event_handler, daemon=True, name='event_handler'),
            progress_bar = Thread(target=self.progbar_track, daemon=True, name='progbar_track')
        )
        self.monitor.event_handler.start()
        self.monitor.progress_bar.start()
        
    def __init_position__(self):

        self.frames.basic_volume.anchor(tk.CENTER)
        self.frames.basic.anchor(tk.CENTER)

        self.frames.playlist.grid(sticky=tk.NSEW, padx=(24, 0), pady=(16, 8))
        self.frames.progress.grid(sticky=tk.NSEW, padx=24, pady=(8, 0))
        self.frames.basic.grid(sticky=tk.NSEW, padx=24, pady=(0, 16))
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.frames.playlist_label.grid(sticky=tk.NSEW)
        self.frames.playlist_canvas.grid(sticky=tk.NSEW)
        self.units.scroll_bar.grid(row=0, column=1, rowspan=2, padx=(0, 7), sticky=tk.NSEW)
        self.frames.playlist.grid_columnconfigure(0, weight=1)
        self.frames.playlist.grid_rowconfigure(1, weight=1)
        self.cfgIDs.playlist_frame = self.frames.playlist_canvas.create_window((0, 0), anchor=tk.NW, window=self.frames.playlist_frame)
        self.frames.playlist_frame.grid_columnconfigure(0, weight=1)

        self.units.button_shuffle.grid(row=0, column=1)
        self.units.button_repeat.grid(row=0, column=2)
        self.units.button_stop.grid(row=0, column=3)
        self.units.button_prev.grid(row=0, column=4)
        self.units.button_play.grid(row=0, column=5)
        self.units.button_next.grid(row=0, column=6)
        self.frames.basic_volume.grid(row=0, column=7, columnspan=1, sticky=tk.NSEW)
        self.units.button_volume.grid(row=0, column=0)
        self.units.optbar_volume.grid(row=0, column=1)

        self.units.label_progress.grid(row=0, column=0, sticky=tk.NSEW, ipadx=4)
        self.units.optbar_progress.grid(row=0, column=1, sticky=tk.NSEW)
        self.frames.progress.grid_columnconfigure(1, weight=1)

        tk.Label(self.frames.playlist_label, text='Name', anchor=tk.W, width=40).grid(row=0, column=0, padx=(1, 0.5), pady=1, sticky=tk.NSEW)
        tk.Label(self.frames.playlist_label, text='Length', anchor=tk.W, width=10).grid(row=0, column=1, padx=(0.5, 1), pady=1, sticky=tk.NSEW)
        self.frames.playlist_label.grid_columnconfigure(0, weight=4)
        self.frames.playlist_label.grid_columnconfigure(1, weight=1)

        self.window.update_idletasks()

        return self

    def __init_appearance__(self):
        
        self.frames.basic.update()
        self.cfgIDs.button_play = self.units.button_play.create_image(self.units.button_play.winfo_width()/2, self.units.button_play.winfo_height()/2, image=self.images.button_play)
        self.cfgIDs.button_stop = self.units.button_stop.create_image(self.units.button_stop.winfo_width()/2, self.units.button_stop.winfo_height()/2, image=self.images.button_stop)
        self.cfgIDs.button_prev = self.units.button_prev.create_image(self.units.button_prev.winfo_width()/2, self.units.button_prev.winfo_height()/2, image=self.images.button_prev)
        self.cfgIDs.button_next = self.units.button_next.create_image(self.units.button_next.winfo_width()/2, self.units.button_next.winfo_height()/2, image=self.images.button_next)
        self.cfgIDs.button_shuffle = self.units.button_shuffle.create_image(self.units.button_shuffle.winfo_width()/2, self.units.button_shuffle.winfo_height()/2, image=self.images.button_shuffle[0])
        self.cfgIDs.button_repeat = self.units.button_repeat.create_image(self.units.button_repeat.winfo_width()/2, self.units.button_repeat.winfo_height()/2, image=self.images.button_repeat[0])
        self.cfgIDs.button_volume = self.units.button_volume.create_image(self.units.button_volume.winfo_width()/2, self.units.button_volume.winfo_height()/2, image=self.images.button_volume[2])

        return self

    def __init_behavior__(self):

        self.frames.playlist_label.bind('<Configure>', self.window_resize)
        self.units.button_volume.bind('<Button-1>', self.toggle_muted)
        self.units.button_play.bind('<Button-1>', self.play_music)
        self.units.button_stop.bind('<Button-1>', self.stop_music)
        self.units.button_prev.bind('<Button-1>', self.prev_song)
        self.units.button_next.bind('<Button-1>', self.next_song)
        self.units.button_repeat.bind('<Button-1>', partial(self.toggle_states, attribute='repeat'))
        self.units.button_shuffle.bind('<Button-1>', partial(self.toggle_states, attribute='random'))
        self.units.optbar_progress.bind('<Button-1>', partial(self.toggle_states, attribute='isdragging'))
        self.units.optbar_progress.bind('<ButtonRelease-1>', self.progbar_moved)
        self.units.button_play.bind('<Enter>', self.hover_on)
        self.units.button_stop.bind('<Enter>', self.hover_on)
        self.units.button_prev.bind('<Enter>', self.hover_on)
        self.units.button_next.bind('<Enter>', self.hover_on)
        self.units.button_shuffle.bind('<Enter>', self.hover_on)
        self.units.button_repeat.bind('<Enter>', self.hover_on)
        self.units.button_volume.bind('<Enter>', self.hover_on)
        self.units.button_play.bind('<Leave>', self.hover_off)
        self.units.button_stop.bind('<Leave>', self.hover_off)
        self.units.button_prev.bind('<Leave>', self.hover_off)
        self.units.button_next.bind('<Leave>', self.hover_off)
        self.units.button_shuffle.bind('<Leave>', self.hover_off)
        self.units.button_repeat.bind('<Leave>', self.hover_off)
        self.units.button_volume.bind('<Leave>', self.hover_off)
        self.states.pointer.trace_add('write', self.pointer_moved)

        return self

    def play_music(self, event=..., status: Literal['playing', 'pause', 'stop'] = ...):
        match self.states.status if (status is Ellipsis) else status:
            case 'playing':
                pygame.mixer.music.pause()
                self.units.button_play.itemconfig(self.cfgIDs.button_play, image=self.images.button_play)
                self.states.status = 'pause'
            case 'pause':
                pygame.mixer.music.unpause()
                self.units.button_play.itemconfig(self.cfgIDs.button_play, image=self.images.button_pause)
                self.states.status = 'playing'
            case 'stop':
                if self.queue:
                    pointer = self.states.pointer.get()
                    self.states.pointer.set(0) if pointer < 0 else ...
                    pygame.mixer.music.play()
                    self.units.button_play.itemconfig(self.cfgIDs.button_play, image=self.images.button_pause)
                    self.states.status = 'playing'
                else:
                    console.info('There is no music in your playlist!')
            case _:
                raise Exception('An unexpected status was detected.')
    
    def stop_music(self, event=...):
        pygame.mixer.music.rewind()
        pygame.mixer.music.pause()
        self.units.button_play.itemconfig(self.cfgIDs.button_play, image=self.images.button_play)
        self.states.status = 'stop'
        
    def add_song(self):

        for file in filedialog.askopenfilenames(filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))):  # 如果有選擇歌曲
            file = AudioFile(self, self.frames.playlist_frame, path=file)
            file.frame.grid(sticky=tk.NSEW)
            self.queue.append(file)  # 將歌曲加入歌曲清單
            console.info('Successfully added the audio to the playlist!')
            
        self.frames.playlist_canvas.itemconfig(
            tagOrId = self.cfgIDs.playlist_frame,
            width = self.frames.playlist_canvas.winfo_width()
        )
        self.frames.playlist.update_idletasks()
        self.frames.playlist_canvas.config(scrollregion=self.frames.playlist_canvas.bbox(tk.ALL))
    
    def adjust_volume(self, event=...):
        value = self.states.volume.get()
        pygame.mixer.music.set_volume(value/100) if self.volume.__ne__(value) else ...
        self.volume = value
        self.units.button_volume.itemconfig(
            tagOrId = self.cfgIDs.button_volume,
            image = self.images.button_volume[2 if (self.volume >= 50) else 1 if (self.volume > 0) else 0]
        )
    
    def toggle_muted(self, event=...):
        if pygame.mixer.music.get_volume() and self.volume: # audible -> muted
            pygame.mixer.music.set_volume(0)
            self.states.volume.set(0)
            self.units.button_volume.itemconfig(self.cfgIDs.button_volume, image=self.images.button_volume[0])
        else:
            if self.volume: # muted -> unmuted
                ...
            else: # silent -> unmuted
                self.volume = 100
                
            pygame.mixer.music.set_volume(self.volume/100)
            self.states.volume.set(self.volume)
            self.units.button_volume.itemconfig(
                tagOrId = self.cfgIDs.button_volume,
                image = self.images.button_volume[2 if (self.volume >= 50) else 1 if (self.volume > 0) else 0]
            )
        
    def hover_on(self, event=...):
        widget: tk.Canvas | tk.Frame = event.widget
        widget.hover = True
        self.states.hover = self.hover(
            widget = widget,
            bgcolor = widget.cget('background'),
            child = self.hover()
        )
        
        if widget.winfo_name().startswith('playlist-audio'):
            fg = bg = None
            for child in widget.grid_slaves():
                if not isinstance(child, tk.Label): continue
                fg = child.cget('foreground')
                bg = child.cget('background')
                font = child.cget('font')
                child.config(fg=color.white, bg=color.dimgray)
            self.states.hover.child.fgcolor = fg
            self.states.hover.child.bgcolor = bg
            self.states.hover.child.font = font
            widget.config(bg=color.dimgray)
        else:
            widget.config(bg=color.lightgray)

    def hover_off(self, event=...):
        try:
            widget: tk.Canvas | tk.Frame = event.widget
            widget.hover = False
            if widget.winfo_name().startswith('playlist-audio'):
                for child in widget.grid_slaves():
                    if not isinstance(child, tk.Label): continue
                    child.config(
                        fg = self.states.hover.child.fgcolor,
                        bg = self.states.hover.child.bgcolor,
                        font = self.states.hover.child.font
                    )

            widget.config(bg=self.states.hover.bgcolor) # @IgnoreException
            self.states.hover = None
        except AttributeError: ...

    # pointer

    def prev_song(self, event=...):
        pointer = self.states.pointer.get()
        if pointer < 0: return

        if self.states.random:
            self.states.pointer.set(
                *sample(
                    array(range(self.queue.length)).filter(lambda _: _.__ne__(pointer)),
                    k = 1
                )
            )

        else:
            pointer -= 1
            pointer = (pointer + self.queue.length) if pointer < 0 else pointer
            self.states.pointer.set(pointer)
            
        self.play_music(status='stop')

    def next_song(self, event=...):
        pointer = self.states.pointer.get()
        if pointer < 0: return

        if self.states.random:
            try:
                self.states.pointer.set(
                    *sample( # @IgnoreException
                        array(range(self.queue.length)).filter(lambda _: _.__ne__(pointer)),
                        k = 1
                    )
                )
            except ValueError:
                self.states.pointer.set(pointer)

        else:
            pointer += 1
            pointer = (pointer - self.queue.length) if pointer >= self.queue.length else pointer
            self.states.pointer.set(pointer)

        self.play_music(status='stop')

    def pointer_moved(self, *args, **kwargs):
        file: AudioFile = self.queue[self.states.pointer.get()]
        file.trigger(cause_pointer_moved=True) if id(self.states.selected) != id(file) else ...
        pygame.mixer.music.unload()
        pygame.mixer.music.load(file.data.path)
        self.progbar_sync(0, file)
        self.states.diff = 0
        console.info(f'loaded - [{Gadget.timeformat(file.data.length)}] {file.data.name}')

    def event_handler(self):
        while True:
            if pygame.event.wait().type != eventID.music_end: continue

            pointer = self.states.pointer.get()
            self.states.status = 'stop'
            match self.states.repeat:
                case 1:
                    pygame.mixer.music.rewind()
                    self.play_music(status='stop')
                case 0 | 2 if ((pointer + 1) < self.queue.length) or self.states.random:
                    self.next_song()
                case 2:
                    self.states.pointer.set(0)
                    self.play_music(status='stop')
                case 0:
                    self.queue[pointer].selected.set(False)
                    self.states.pointer.set(0)
                    self.units.button_play.itemconfig(
                        tagOrId = self.cfgIDs.button_play,
                        image = self.images.button_play
                    )

    # progess bar

    def progbar_sync(self, pct: float, file: AudioFile, reposition: bool = True):
        """The parameter `pct` must be the value of percentage type
        in #.* format, rather than the *% one."""

        time = pct * file.data.length
        
        try: pygame.mixer.music.set_pos(time) if reposition else ... # @IgnoreException

        except pygame.error: ...

        else:
            return (time - (pygame.mixer.music.get_pos() / 1000))

        finally:
            self.states.progress_pct.set(pct * 100)
            self.units.label_progress.config(text=Gadget.timeformat(time))
        
        return 0

    def progbar_moved(self, event):
        self.states.isdragging = False
        try:
            self.states.diff = self.progbar_sync(
                pct = Gadget.round(self.states.progress_pct.get() / 100, '.0000'),
                file = self.queue[self.states.pointer.get()], # @IgnoreException
                reposition = True
            )

        except IndexError: ...

    def progbar_track(self):

        while True:
            sleep(.1)
            while pygame.mixer.music.get_busy() and not self.states.isdragging:

                try:
                    file: AudioFile = self.queue[self.states.pointer.get()]  # @IgnoreException
                    pos = pygame.mixer.music.get_pos() / 1000 + self.states.diff
                    pct = Gadget.round(pos / file.data.length, '.0000') # @IgnoreException
                    self.progbar_sync(
                        pct = pct,
                        file = file,
                        reposition = False
                    )
                    sleep(.01)

                except (IndexError, pygame.error):
                    ...

    # miscellaneous
                    
    def toggle_states(self, event, attribute: Literal['isdragging', 'repeat', 'random']):
        match attribute:
            case 'isdragging':
                self.states.isdragging = False if self.states.isdragging else True
            case 'repeat':
                self.states.repeat += 1 if self.states.repeat < 2 else -2
                self.units.button_repeat.itemconfig(
                    tagOrId = self.cfgIDs.button_repeat,
                    image = self.images.button_repeat[int(self.states.repeat)]
                )
            case 'random':
                self.states.random = False if self.states.random else True
                self.units.button_shuffle.itemconfig(
                    tagOrId = self.cfgIDs.button_shuffle,
                    image = self.images.button_shuffle[int(self.states.random)]
                )
            case _:
                raise Exception('An unknown attribute was given')

    def window_resize(self, event):
        try:
            assert event.widget is self.frames.playlist_label # @IgnoreException
            assert event.width != self.states.playlist_label_width
            self.states.playlist_label_width = event.width
            self.frames.playlist_frame.config(width=event.width)
            self.frames.playlist_canvas.itemconfig(
                tagOrId = self.cfgIDs.playlist_frame,
                width = event.width
            )
        
        except AssertionError: ...

class audio: ...
audio: MusicPlayer = MusicPlayer(tk.Tk())  # 創建音樂播放器物件
audio.window.mainloop()  # 啟動視窗主迴圈，等待使用者操作