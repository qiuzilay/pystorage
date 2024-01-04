from __future__ import annotations
from os import chdir, getcwd
from os.path import dirname, realpath

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

from modules.toolbox import array, Enum, Gadget, console
from dataclasses import dataclass, field
from typing import Literal
import matplotlib as plt
import tkinter.ttk as ttk
import tkinter as tk

class color(Enum):
    white = '#FFFFFF'
    red = '#FF0000'
    black = '#000000'

class Window():

    def __new__(cls):

        @dataclass
        class __frames__:
            main: tk.LabelFrame = None
            main_panel: tk.Frame = None
            main_button: tk.Frame = None
            main_display: tk.Frame = None
            side: tk.LabelFrame = None

        @dataclass
        class __units__:
            label_apr: tk.Label
            label_year: tk.Label
            label_loan: tk.Label
            label_mpymt: tk.Label
            label_tpymt: tk.Label
            label_mpymt_val: tk.Label
            label_tpymt_val: tk.Label
            entry_apr: tk.Entry
            entry_year: tk.Entry
            entry_loan: tk.Entry
            btn_calc: tk.Button
            btn_clear: tk.Button

        class __const__(Enum):
            text_btn_calc = '計算貸款金額'
            text_btn_clear = '清除'


        cls.frames = __frames__
        cls.units = __units__
        cls.const = __const__
        
        return super().__new__(cls)

    def __init__(self):

        self.root = tk.Tk()
        self.root.title('Loan Calculator')
        self.root.iconbitmap('')
        self.root.geometry(Gadget.getGeometry(self.root, width=1280, height=720))
        self.root.option_add('*font', ('Microsoft JhengHei', 10, 'normal'))

        self.__init_buildtree__()

    def __init_buildtree__(self):

        self.frames = self.frames(
            main = tk.LabelFrame(self.root, text='資料輸入區'),
            side = tk.LabelFrame(self.root, text='滑桿選擇區')
        )
        self.frames.main_panel = tk.Frame(self.frames.main)
        self.frames.main_button = tk.Frame(self.frames.main, bg='red')
        self.frames.main_display = tk.Frame(self.frames.main)

        self.units = self.units(
            label_apr = tk.Label(self.frames.main_panel, text='貸款年利率', anchor=tk.W),
            label_year = tk.Label(self.frames.main_panel, text='貸款年數', anchor=tk.W),
            label_loan = tk.Label(self.frames.main_panel, text='貸款金額', anchor=tk.W),
            label_mpymt = tk.Label(self.frames.main_panel, text='月付款金額', anchor=tk.W),
            label_tpymt = tk.Label(self.frames.main_panel, text='總付款金額', anchor=tk.W),
            entry_apr = tk.Entry(self.frames.main_panel, justify=tk.RIGHT),
            entry_year = tk.Entry(self.frames.main_panel, justify=tk.RIGHT),
            entry_loan = tk.Entry(self.frames.main_panel, justify=tk.RIGHT),
            label_mpymt_val = tk.Label(self.frames.main_panel, anchor=tk.E),
            label_tpymt_val = tk.Label(self.frames.main_panel, anchor=tk.E),
            btn_calc = tk.Button(self.frames.main_button, text=self.const.text_btn_calc, relief=tk.GROOVE),
            btn_clear = tk.Button(self.frames.main_button, text=self.const.text_btn_clear, relief=tk.GROOVE)
        )

        return self.__init_position__()
    
    def __init_position__(self):

        self.frames.main.grid(row=0, column=0, sticky=tk.NSEW, padx=(16, 8), pady=16)
        self.frames.side.grid(row=0, column=1, sticky=tk.NSEW, padx=(8, 16), pady=16)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=4)
        self.root.grid_columnconfigure(1, weight=1)

        self.frames.main_panel.grid(row=0, column=0, sticky=tk.NSEW)
        self.frames.main_button.grid(row=1, column=0, sticky=tk.NSEW)
        self.frames.main_display.grid(row=2, column=0, sticky=tk.NSEW)
        self.frames.main.grid_columnconfigure(0, weight=1)
        self.frames.main.grid_rowconfigure(0, weight=25)
        self.frames.main.grid_rowconfigure(1, weight=5)
        self.frames.main.grid_rowconfigure(2, weight=70)

        self.units.label_apr.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 96)); self.units.entry_apr.grid(row=0, column=1, sticky=tk.NSEW)
        self.units.label_year.grid(row=1, column=0, sticky=tk.NSEW, padx=(0, 96)); self.units.entry_year.grid(row=1, column=1, sticky=tk.NSEW)
        self.units.label_loan.grid(row=2, column=0, sticky=tk.NSEW, padx=(0, 96)); self.units.entry_loan.grid(row=2, column=1, sticky=tk.NSEW)
        self.units.label_mpymt.grid(row=3, column=0, sticky=tk.NSEW, padx=(0, 96)); self.units.label_mpymt_val.grid(row=3, column=1, sticky=tk.NSEW)
        self.units.label_tpymt.grid(row=4, column=0, sticky=tk.NSEW, padx=(0, 96)); self.units.label_tpymt_val.grid(row=4, column=1, sticky=tk.NSEW)
        
        self.units.btn_calc.grid(row=0, column=0, sticky=tk.E, padx=(0, 16))
        self.units.btn_clear.grid(row=0, column=1, sticky=tk.W, padx=(16, 0))
        self.frames.main_button.grid_rowconfigure(0, weight=1)
        self.frames.main_button.grid_columnconfigure(0, weight=1)
        self.frames.main_button.grid_columnconfigure(1, weight=1)

        self.root.update_idletasks()

        return self.__init_configure__()
    
    def __init_configure__(self):
        
        _ = max(len(self.const.text_btn_calc), len(self.const.text_btn_clear))
        self.units.btn_calc.config(text=self.const.text_btn_calc.center(_, '\u3000'))
        self.units.btn_clear.config(text=self.const.text_btn_clear.center(_, '\u3000'))

        self.root.update_idletasks()

        return self

Window().root.mainloop()