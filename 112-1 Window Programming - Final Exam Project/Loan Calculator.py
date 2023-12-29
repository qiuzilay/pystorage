from __future__ import annotations
from modules.toolbox import array, console
from dataclasses import dataclass, field
from typing import Literal
import tkinter as tk
import matplotlib as plt

class Window():

    def __new__(cls):

        @dataclass
        class frames:
            main: tk.Frame = None
            main_btn: tk.Frame = None
            main_panel: tk.Text = None
            side: tk.Frame = None

        @dataclass
        class units:
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

        cls.frames = frames
        cls.units = units
        
        return super().__new__(cls)


    def __init__(self):

        self.root = tk.Tk()

        self.__init_buildtree__()


    def __init_buildtree__(self):

        self.frames = self.frames(
            main = tk.Frame(self.root),
            side = tk.Frame(self.root)
        )
        self.frames.main_btn = tk.Frame(self.frames.main)
        self.frames.main_panel = tk.Frame(self.frames.main)

        self.units = self.units(
            label_apr = tk.Label(self.frames.main, text='貸款年利率'),
            label_year = tk.Label(self.frames.main, text='貸款年數'),
            label_loan = tk.Label(self.frames.main, text='貸款金額'),
            label_mpymt = tk.Label(self.frames.main, text='月付款金額'),
            label_tpymt = tk.Label(self.frames.main, text='總付款金額'),
            entry_apr = tk.Entry(self.frames.main),
            entry_year = tk.Entry(self.frames.main),
            entry_loan = tk.Entry(self.frames.main),
            label_mpymt_val = tk.Label(self.frames.main),
            label_tpymt_val = tk.Label(self.frames.main),
            btn_calc = tk.Button(self.frames.main_btn),
            btn_clear = tk.Button(self.frames.main_btn)
        )
        return self


Window().root.mainloop()