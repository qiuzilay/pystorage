from __future__ import annotations
from os import chdir, getcwd
from os.path import dirname, realpath, basename

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

from modules.toolbox import Gadget, Enum, array, console
from dataclasses import dataclass, field
from collections import namedtuple as ntuple
from typing import Literal
from decimal import Decimal, ROUND_HALF_UP
from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as filedialog
import pygame  # 引入Pygame模組，用於音樂播放
import enum

class color(Enum):
    white = '#FFFFFF'
    lightgray = '#D3D3D3'
    dimgray = '#696969'
    darkgray = '#404040'
    black = '#000000'
    transparent = '#010101'

class font(Enum):
    default = ('Microsoft JhengHei', 10, 'normal')
    bold = ('Microsoft JhengHei', 10, 'bold')

class AudioFile:
    
    def __init__(self, root: MusicPlayer, parent: tk.Tk | tk.Frame, path: str):
        
        self.root = root
        self.root.states.count += 1
        self.id = self.root.states.count
        self.selected = False
        self.frame = tk.Frame(parent, name=f'playlist-audio_{self.id}', bg=color.white)

        @dataclass
        class metadata:
            name: str
            path: str
            length: int

        self.data = metadata(
            name = basename(path),
            path = realpath(path),
            length = int(Gadget.round(pygame.mixer.Sound(path).get_length(), format='0'))
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

        self.frame.bind('<Enter>', root.hover_on)
        self.frame.bind('<Leave>', root.hover_off)
        self.frame.bind('<Double-Button-1>', self.trigger)
        self.labels.name.bind('<Double-Button-1>', self.trigger)
        self.labels.length.bind('<Double-Button-1>', self.trigger)

        console.info(id(self.trigger))

        @dataclass
        class color_info:
            bgcolor: object = None
            fgcolor: object = None

        @dataclass
        class default_style:
            frame = color_info(bgcolor=self.frame.cget('background'))
            label = color_info(bgcolor=self.labels.name.cget('background'), fgcolor=self.labels.name.cget('foreground'))

        self.default_style = default_style()


    def trigger(self, event):
        widget: tk.Frame | tk.Label = event.widget
        widget = widget if isinstance(widget, tk.Frame) else widget.master
        console.info(widget.winfo_name(), self.id)
        console.info((self.selected, bool(self.root.states.focus)))
        match (self.selected, bool(self.root.states.focus)):
            case (True, True):
                self.unfocused()
                self.root.states.focus = None
                self.root.states.hover.bgcolor = self.default_style.frame.bgcolor
                self.root.states.hover.child.bgcolor = self.default_style.label.bgcolor
                self.root.states.hover.child.fgcolor = self.default_style.label.fgcolor
            case (True, False):
                raise Exception('An impossible situation occurred.')
            case (False, True):
                self.root.states.focus.unfocused()
                self.focused()
                self.root.states.focus = self
            case (False, False):
                self.focused()
                self.root.states.focus = self

    def focused(self):
        console.info(self.frame.winfo_name(), 'focused!')
        self.selected = True
        self.frame.config(bg=color.darkgray)
        self.labels.name.config(bg=color.darkgray, fg=color.white)
        self.labels.length.config(bg=color.darkgray, fg=color.white)
        self.root.states.hover.bgcolor = color.darkgray
        self.root.states.hover.child.bgcolor = color.darkgray
        self.root.states.hover.child.fgcolor = color.white

    def unfocused(self):
        console.info(self.frame.winfo_name(), 'unfocused!')
        self.selected = False
        self.frame.config(bg=self.default_style.frame.bgcolor)
        self.labels.name.config(bg=self.default_style.label.bgcolor, fg=color.black)
        self.labels.length.config(bg=self.default_style.label.bgcolor, fg=color.black)
        

class MusicPlayer:

    def __init__(self, window:tk.Tk):

        @dataclass
        class frames: # frameworks
            menu: tk.Menu = tk.Menu(window)
            label: tk.Frame = tk.Frame(window, bg=color.white)
            playlist: tk.Frame = tk.Frame(window, bg=color.white)
            basic: tk.Frame = tk.Frame(window)
            volume: tk.Frame = None # child of frames.basic
            file: tk.Menu = None # child of frams.menu

        @dataclass
        class units:
            button_play: tk.Canvas
            button_stop: tk.Canvas
            button_prev: tk.Canvas
            button_next: tk.Canvas
            button_repeat: tk.Canvas
            button_shuffle: tk.Canvas
            button_volume: tk.Canvas
            optbar_volume: ttk.Scale
        
        @dataclass
        class hover_info:
            widget: tk.Widget = None
            fgcolor: object = None
            bgcolor: object = None
            child: hover_info = None

        @dataclass
        class images:
            button_play: tk.PhotoImage = tk.PhotoImage(file='./images/button_play 128x.png').subsample(2)
            button_pause: tk.PhotoImage = tk.PhotoImage(file='./images/button_pause 128x.png').subsample(2)
            button_prev: tk.PhotoImage = tk.PhotoImage(file='./images/button_previous 128x.png').subsample(3)
            button_next: tk.PhotoImage = tk.PhotoImage(file='./images/button_next 128x.png').subsample(3)
            button_stop: tk.PhotoImage = tk.PhotoImage(file='./images/button_stop 128x.png').subsample(4)
            button_repeat: tk.PhotoImage = tk.PhotoImage(file='./images/button_repeat.png').subsample(4)
            button_shuffle: tk.PhotoImage = tk.PhotoImage(file='./images/button_shuffle.png').subsample(4)
            button_volume: tuple[tk.PhotoImage, ...] = (
                tk.PhotoImage(file='./images/volume_0.png').subsample(4),
                tk.PhotoImage(file='./images/volume_1.png').subsample(4),
                tk.PhotoImage(file='./images/volume_2.png').subsample(4)
            )

        @dataclass
        class states:
            status: Literal['playing', 'pause', 'stop'] = 'stop'
            pointer: int = 0
            count: int = 0
            focus: AudioFile | None = None
            hover: hover_info = hover_info
            volume: tk.IntVar = field(default_factory=tk.IntVar)
            
        btnsize = Gadget.scaler(80)
        
        self.window = window
        self.volume = 100
        self.queue = array()
        self.states = states()
        self.images = images()
        self.frames = frames()
        self.frames.volume = tk.Frame(self.frames.basic)
        self.frames.file = tk.Menu(self.frames.menu, tearoff=False)
        self.units = units(
            button_play = tk.Canvas(self.frames.basic, width=int(btnsize), height=int(btnsize)),
            button_prev = tk.Canvas(self.frames.basic, width=int(btnsize*0.75), height=int(btnsize*0.75)),
            button_next = tk.Canvas(self.frames.basic, width=int(btnsize*0.75), height=int(btnsize*0.75)),
            button_stop = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_repeat = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_shuffle = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_volume = tk.Canvas(self.frames.volume, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            optbar_volume = ttk.Scale(self.frames.volume, from_=0, to=100, variable=self.states.volume, length=int(btnsize), command=self.adjust_volume)
        )

        minsize = Gadget.getGeometry(window, width=360, height=480, output='metadata')
        
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume/100)
        self.states.volume.set(self.volume)
        self.window.title('Simple Music Player')
        self.window.iconbitmap('mediaplayer.ico')
        self.window.geometry(Gadget.getGeometry(window, width=540, height=720))
        self.window.minsize(width=minsize.width, height=minsize.height)
        self.window.config(menu=self.frames.menu)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.option_add('*font', font.default)
        self.window.wm_attributes('-topmost', True)
        self.window.wm_attributes('-transparentcolor', color.transparent)

        self.frames.file.add_command(label='Import', command=self.add_song)
        self.frames.menu.add_cascade(label='File', menu=self.frames.file)
        
        self.__init_position__()\
            .__init_appearance__()\
            .__init_behavior__()
        
    def __init_position__(self):
        self.frames.volume.anchor(tk.CENTER)
        self.frames.basic.anchor(tk.CENTER)

        self.frames.label.grid(sticky=tk.NSEW, padx=16, pady=(16, 0))
        self.frames.playlist.grid(sticky=tk.NSEW, padx=16, pady=(0, 8))
        self.frames.basic.grid(sticky=tk.NSEW, padx=16, pady=(8, 16))

        self.units.button_shuffle.grid(row=0, column=1)
        self.units.button_repeat.grid(row=0, column=2)
        self.units.button_stop.grid(row=0, column=3)
        self.units.button_prev.grid(row=0, column=4)
        self.units.button_play.grid(row=0, column=5)
        self.units.button_next.grid(row=0, column=6)
        self.frames.volume.grid(row=0, column=7, columnspan=1, sticky=tk.NSEW)
        self.units.button_volume.grid(row=0, column=0)
        self.units.optbar_volume.grid(row=0, column=1)

        tk.Label(self.frames.label, text='Name', anchor=tk.W, width=40).grid(row=0, column=0, padx=(1, 0.5), pady=1, sticky=tk.NSEW)
        tk.Label(self.frames.label, text='Length', anchor=tk.W, width=10).grid(row=0, column=1, padx=(0.5, 1), pady=1, sticky=tk.NSEW)
        self.frames.label.columnconfigure(0, weight=4)
        self.frames.label.columnconfigure(1, weight=1)
        self.frames.playlist.columnconfigure(0, weight=1)

        return self

    def __init_appearance__(self):

        @dataclass
        class cfgIDs:
            button_play: int
            button_stop: int
            button_prev: int
            button_next: int
            button_shuffle: int
            button_repeat: int
            button_volume: int
        
        self.frames.basic.update()
        self.cfgIDs = cfgIDs(
            button_play = self.units.button_play.create_image(self.units.button_play.winfo_width()/2, self.units.button_play.winfo_height()/2, image=self.images.button_play),
            button_stop = self.units.button_stop.create_image(self.units.button_stop.winfo_width()/2, self.units.button_stop.winfo_height()/2, image=self.images.button_stop),
            button_prev = self.units.button_prev.create_image(self.units.button_prev.winfo_width()/2, self.units.button_prev.winfo_height()/2, image=self.images.button_prev),
            button_next = self.units.button_next.create_image(self.units.button_next.winfo_width()/2, self.units.button_next.winfo_height()/2, image=self.images.button_next),
            button_shuffle = self.units.button_shuffle.create_image(self.units.button_shuffle.winfo_width()/2, self.units.button_shuffle.winfo_height()/2, image=self.images.button_shuffle),
            button_repeat = self.units.button_repeat.create_image(self.units.button_repeat.winfo_width()/2, self.units.button_repeat.winfo_height()/2, image=self.images.button_repeat),
            button_volume = self.units.button_volume.create_image(self.units.button_volume.winfo_width()/2, self.units.button_volume.winfo_height()/2, image=self.images.button_volume[2])
        )
        
        return self

    def __init_behavior__(self):
        self.units.button_volume.bind('<Button-1>', self.toggle_muted)
        self.units.button_play.bind('<Button-1>', self.play_music)
        self.units.button_stop.bind('<Button-1>', self.stop_music)
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
        
        return self

    def play_music(self, event):
        match self.states.status:
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
                    file: AudioFile = self.queue[self.states.pointer]
                    pygame.mixer.music.load(file.data.path)
                    pygame.mixer.music.play()
                    self.units.button_play.itemconfig(self.cfgIDs.button_play, image=self.images.button_pause)
                    self.states.status = 'playing'
                else:
                    console.info('There is no music in your playlist!')
            case _:
                raise Exception('An unexpected status was detected.')
    
    def stop_music(self, event):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()  # 停止播放歌曲
            self.units.button_play.itemconfig(self.cfgIDs.button_play, image=self.images.button_play)
            self.states.status = 'stop'
        else:
            console.info('There is no playing music to stop!')
        
    def add_song(self):
        file = filedialog.askopenfilename(filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*")))  # 選擇要加入的MP3格式歌曲
        if file:  # 如果有選擇歌曲
            file = AudioFile(self, self.frames.playlist, path=file)
            self.queue.append(file)  # 將歌曲加入歌曲清單
            file.frame.grid(sticky=tk.NSEW)
            console.info('Successfully added the audio to the playlist!')
            #self.frames.playlist.insert(tk.END, basename(file))  # 將歌曲名稱顯示在Listbox中
    
    def adjust_volume(self, event):
        value = self.states.volume.get()
        pygame.mixer.music.set_volume(value/100) if self.volume.__ne__(value) else ...
        self.volume = value
        self.units.button_volume.itemconfig(
            tagOrId = self.cfgIDs.button_volume,
            image = self.images.button_volume[2 if (self.volume >= 50) else 1 if (self.volume > 0) else 0]
        )
    
    def toggle_muted(self, event):
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
        
    def hover_on(self, event):
        widget: tk.Canvas | tk.Frame = event.widget
        self.states.hover = self.states.hover(
            widget = widget,
            bgcolor = widget.cget('background'),
            child = self.states.hover()
        )
        
        if widget.winfo_name().startswith('playlist-audio'):
            fg = bg = None
            for child in widget.grid_slaves():
                if not isinstance(child, tk.Label): continue
                fg = child.cget('foreground')
                bg = child.cget('background')
                child.config(fg=color.white, bg=color.dimgray)
            self.states.hover.child.fgcolor = fg
            self.states.hover.child.bgcolor = bg
            widget.config(bg=color.dimgray)
        else:
            widget.config(bg=color.lightgray)

    def hover_off(self, event):
        widget: tk.Canvas | tk.Frame = event.widget

        if widget.winfo_name().startswith('playlist-audio'):
            for child in widget.grid_slaves():
                if not isinstance(child, tk.Label): continue
                child.config(
                    fg = self.states.hover.child.fgcolor,
                    bg = self.states.hover.child.bgcolor
                )

        widget.config(bg=self.states.hover.bgcolor)
        self.states.hover = self.states.hover.__class__

        
class audio: ...

audio: MusicPlayer = MusicPlayer(tk.Tk())  # 創建音樂播放器物件
audio.window.mainloop()  # 啟動視窗主迴圈，等待使用者操作