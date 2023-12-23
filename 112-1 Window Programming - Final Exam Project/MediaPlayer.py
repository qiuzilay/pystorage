from os import chdir, getcwd
from os.path import dirname, realpath, basename

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

from modules.toolbox import Gadget, Enum, array, console
from dataclasses import dataclass, astuple
from collections import namedtuple as ntuple
from tkinter import ttk
import tkinter as tk
import tkinter.filedialog as filedialog
import pygame  # 引入Pygame模組，用於音樂播放
import enum

class color(Enum):
    lightgray = '#D3D3D3'
    dimgray = '#696969'
    transparent = '#010101'

class AudioFile:
    
    def __init__(self, parent: tk.Tk | tk.Frame | tk.PanedWindow, path: str):
        
        @dataclass
        class file:
            name: str = None
            path: str = None
            length: int = None

        self.file = file(path=realpath(path))
        self.frame = tk.Frame(parent)

class MusicPlayer:

    def __init__(self, window:tk.Tk):

        @dataclass
        class frames: # frameworks
            basic: tk.Frame = tk.Frame(window)
            playlist: tk.LabelFrame = tk.LabelFrame(window, text=' 播放清單 ', font=('Microsoft JhengHei', 12, 'normal'))
            volume: tk.Frame = None

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

        class configs(Enum):
            volume = tk.IntVar(value=100)
            
        btnsize = Gadget.scaler(80)
        
        self.window = window
        self.queue = array()
        self.pointer = 0
        self.hover = ntuple('hover', ('widget', 'bgcolor'))
        self.configs = configs
        self.volume = self.configs.volume.get()
        self.images = images()
        self.frames = frames()
        self.frames.volume = tk.Frame(self.frames.basic)
        self.units = units(
            button_play = tk.Canvas(self.frames.basic, width=int(btnsize), height=int(btnsize)),
            button_prev = tk.Canvas(self.frames.basic, width=int(btnsize*0.75), height=int(btnsize*0.75)),
            button_next = tk.Canvas(self.frames.basic, width=int(btnsize*0.75), height=int(btnsize*0.75)),
            button_stop = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_repeat = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_shuffle = tk.Canvas(self.frames.basic, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            button_volume = tk.Canvas(self.frames.volume, width=int(btnsize*0.5), height=int(btnsize*0.5)),
            optbar_volume = ttk.Scale(self.frames.volume, from_=0, to=100, variable=self.configs.volume, length=int(btnsize), command=self.adjust_volume)
        )

        minsize = Gadget.getGeometry(window, width=360, height=480, output='metadata')

        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume/100)
        self.window.title('Simple Music Player')
        self.window.iconbitmap('mediaplayer.ico')
        self.window.geometry(Gadget.getGeometry(window, width=540, height=720))
        self.window.minsize(width=minsize.width, height=minsize.height)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.wm_attributes('-topmost', True)
        self.window.wm_attributes('-transparentcolor', color.transparent)

        self.frames.playlist.grid(sticky=tk.NSEW, padx=16, pady=(16, 8))
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

        self.frames.volume.anchor(tk.CENTER)
        self.frames.basic.anchor(tk.CENTER)

        self.frames.basic.update()
        
        @dataclass
        class cfgIDs:
            button_play: int = self.units.button_play.create_image(self.units.button_play.winfo_width()/2, self.units.button_play.winfo_height()/2, image=self.images.button_play)
            button_stop: int = self.units.button_stop.create_image(self.units.button_stop.winfo_width()/2, self.units.button_stop.winfo_height()/2, image=self.images.button_stop)
            button_prev: int = self.units.button_prev.create_image(self.units.button_prev.winfo_width()/2, self.units.button_prev.winfo_height()/2, image=self.images.button_prev)
            button_next: int = self.units.button_next.create_image(self.units.button_next.winfo_width()/2, self.units.button_next.winfo_height()/2, image=self.images.button_next)
            button_shuffle: int = self.units.button_shuffle.create_image(self.units.button_shuffle.winfo_width()/2, self.units.button_shuffle.winfo_height()/2, image=self.images.button_shuffle)
            button_repeat: int = self.units.button_repeat.create_image(self.units.button_repeat.winfo_width()/2, self.units.button_repeat.winfo_height()/2, image=self.images.button_repeat)
            button_volume: int = self.units.button_volume.create_image(self.units.button_volume.winfo_width()/2, self.units.button_volume.winfo_height()/2, image=self.images.button_volume[2])
        
        self.cfgIDs = cfgIDs()

        self.units.button_volume.bind('<Button-1>', self.toggle_muted)
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


    def play_music(self):
        if self.queue:  # 確認歌曲清單非空
            pygame.mixer.music.load(self.queue[self.pointer])  # 載入選定的歌曲
            pygame.mixer.music.play()  # 播放歌曲
    
    def pause_music(self):
        pygame.mixer.music.pause()  # 暫停播放歌曲
    
    def stop_music(self):
        pygame.mixer.music.stop()  # 停止播放歌曲
        
    def add_song(self):
        file = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])  # 選擇要加入的MP3格式歌曲
        if file:  # 如果有選擇歌曲
            self.queue.append(file)  # 將歌曲加入歌曲清單
            self.frames.playlist.insert(tk.END, basename(file))  # 將歌曲名稱顯示在Listbox中

    def adjust_volume(self, event):
        value = self.configs.volume.get()
        pygame.mixer.music.set_volume(value/100) if self.volume.__ne__(value) else ...
        self.volume = value
        self.units.button_volume.itemconfig(
            tagOrId = self.cfgIDs.button_volume,
            image = self.images.button_volume[2 if (self.volume >= 50) else 1 if (self.volume > 0) else 0]
        )
    
    def toggle_muted(self, event):
        if pygame.mixer.music.get_volume() and self.volume: # audible -> muted
            pygame.mixer.music.set_volume(0)
            self.configs.volume.set(0)
            self.units.button_volume.itemconfig(self.cfgIDs.button_volume, image=self.images.button_volume[0])
        else:
            if self.volume: # muted -> unmuted
                ...
            else: # silent -> unmuted
                self.volume = 60
                
            pygame.mixer.music.set_volume(self.volume/100)
            self.configs.volume.set(self.volume)
            self.units.button_volume.itemconfig(
                tagOrId = self.cfgIDs.button_volume,
                image = self.images.button_volume[2 if (self.volume >= 50) else 1 if (self.volume > 0) else 0]
            )
        
    def hover_on(self, event):
        canvas: tk.Canvas = event.widget
        self.hover = self.hover(widget=canvas, bgcolor=canvas.cget('background'))
        canvas.config(bg=color.lightgray)

    def hover_off(self, event):
        canvas: tk.Canvas = event.widget
        canvas.config(bg=self.hover.bgcolor)
        self.hover = self.hover.__class__
            
        
        
class audio: ...

audio: MusicPlayer = MusicPlayer(tk.Tk())  # 創建音樂播放器物件
audio.window.mainloop()  # 啟動視窗主迴圈，等待使用者操作