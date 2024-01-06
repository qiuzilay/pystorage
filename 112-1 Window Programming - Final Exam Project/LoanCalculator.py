from __future__ import annotations
from os import chdir, getcwd
from os.path import dirname, realpath

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

from modules.toolbox import array, Enum, Gadget, console
from functools import partial
from dataclasses import dataclass, field
from typing import Literal
import matplotlib as plt
import tkinter.ttk as ttk
import tkinter as tk

class color(Enum):
    white = '#FFFFFF'
    red = '#FF0000'
    black = '#000000'

def linefo(issue, prin, intr, remain) -> str:
    width = 11
    return (str(issue).center(width*2) +
            str(prin).center(width*4) +
            str(intr).center(width*4) +
            str(remain).center(width*4))

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
            btn_calc: ttk.Button
            btn_clear: ttk.Button
            label_panel: tk.Label
            text_panel: tk.Text
            scrollbar_panel: tk.Scrollbar
            scale_apr: ttk.Scale
            scale_year: ttk.Scale
            scale_loan: ttk.Scale
            option_ETP: ttk.Radiobutton
            option_EPP: ttk.Radiobutton
        
        @dataclass
        class __var__:
            mode: tk.StringVar = field(default_factory=tk.StringVar)

        class __const__(Enum):
            text_btn_calc = '計算貸款金額'
            text_btn_clear = '清除'

        cls.frames = __frames__
        cls.units = __units__
        cls.const = __const__
        cls.var = __var__
        
        return super().__new__(cls)

    def __init__(self):

        self.root = tk.Tk()
        self.root.title('Loan Calculator')
        self.root.iconbitmap('')
        self.root.geometry(Gadget.getGeometry(self.root, width=960, height=720))
        self.root.option_add('*font', ('Microsoft JhengHei', 10, 'normal'))

        self.var = self.var()
        self.style = ttk.Style()

        self.__init_buildtree__()

    def __init_buildtree__(self):

        self.frames = self.frames(
            main = tk.LabelFrame(self.root, text='資料輸入區'),
            side = tk.LabelFrame(self.root, text='滑桿選擇區')
        )
        self.frames.main_panel = tk.Frame(self.frames.main)
        self.frames.main_button = tk.Frame(self.frames.main)
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
            btn_calc = ttk.Button(self.frames.main_button, text=self.const.text_btn_calc),
            btn_clear = ttk.Button(self.frames.main_button, text=self.const.text_btn_clear),
            label_panel = tk.Label(self.frames.main_display, anchor=tk.W),
            text_panel = tk.Text(self.frames.main_display, bg=color.white, state=tk.DISABLED),
            scrollbar_panel = tk.Scrollbar(self.frames.main_display),
            scale_apr = ttk.Scale(self.frames.side, from_=0, to=100, orient=tk.VERTICAL),
            scale_year = ttk.Scale(self.frames.side, from_=0, to=100, orient=tk.VERTICAL),
            scale_loan = ttk.Scale(self.frames.side, from_=0, to=100, orient=tk.VERTICAL),
            option_ETP = ttk.Radiobutton(self.frames.side, text='本息平均攤還法', value='ETP', variable=self.var.mode),
            option_EPP = ttk.Radiobutton(self.frames.side, text='本金平均攤還法', value='EPP', variable=self.var.mode)
        )

        return self.__init_position__()
    
    def __init_position__(self):

        # -------- main ---------

        self.frames.main.grid(row=0, column=0, sticky=tk.NSEW, padx=(16, 8), pady=16)
        self.frames.side.grid(row=0, column=1, sticky=tk.NSEW, padx=(8, 16), pady=16)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.frames.main_panel.grid(row=0, column=0, sticky=tk.NSEW)
        self.frames.main_button.grid(row=1, column=0, sticky=tk.NSEW)
        self.frames.main_display.grid(row=2, column=0, sticky=tk.NSEW)
        self.frames.main.grid_columnconfigure(0, weight=1)
        self.frames.main.grid_rowconfigure(2, weight=1)

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

        self.units.label_panel.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        self.units.text_panel.grid(row=1, column=0, sticky=tk.NSEW)
        self.units.scrollbar_panel.grid(row=1, column=1, sticky=tk.NSEW)
        self.frames.main_display.grid_columnconfigure(0, weight=1)

        # -------- side --------

        self.units.scale_apr.grid(row=0, column=0, sticky=tk.NSEW)
        self.units.scale_year.grid(row=0, column=1, sticky=tk.NSEW)
        self.units.scale_loan.grid(row=0, column=2, sticky=tk.NSEW)
        self.units.option_ETP.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
        self.units.option_EPP.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW)
        #self.frames.side.grid_columnconfigure(0, weight=1)
        #self.frames.side.grid_columnconfigure(1, weight=1)
        #self.frames.side.grid_columnconfigure(2, weight=1)

        self.root.update_idletasks()

        return self.__init_behavior__()
    
    def __init_behavior__(self):

        self.var.mode.trace_add('write', lambda *_: console.info(self.var.mode.get()))

        return self.__init_adjustment__()
    
    def __init_adjustment__(self):

        self.units.option_ETP.invoke()
        
        _ = max(len(self.const.text_btn_calc), len(self.const.text_btn_clear))
        self.units.btn_calc.config(text=self.const.text_btn_calc.center(_, '\u3000'))
        self.units.btn_clear.config(text=self.const.text_btn_clear.center(_, '\u3000'))
        
        self.units.label_panel.config(text=linefo('期別', '償還本金', '償還利息', '剩餘本金'))
        self.units.scrollbar_panel.config(command=self.units.text_panel.yview)
        self.units.text_panel.config(yscrollcommand=self.units.scrollbar_panel.set)

        self.root.update_idletasks()

        return self


window = Window()
window.root.mainloop()