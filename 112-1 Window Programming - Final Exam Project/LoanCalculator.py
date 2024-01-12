from __future__ import annotations
from os import chdir, getcwd
from os.path import dirname, realpath

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

from modules.toolbox import array, Enum, Gadget, is_number, is_integer, apchInt, console
from modules.toolbox.interface import terminal, input
from collections import namedtuple as ntuple
from dataclasses import dataclass, field
from functools import partial
from typing import Literal, Callable, Self, Any
import matplotlib.pyplot as plt
import tkinter.ttk as ttk
import tkinter as tk

root = terminal.create()

class color(Enum):
    white = '#FFFFFF'
    red = '#FF0000'
    crimson = '#DC143C'
    black = '#000000'

def linefo(issue, prin, intst, remain) -> str:
    return '\t' + str(issue) + '\t'*2 + str(prin) + '\t'*2 + str(intst) + '\t'*2 + str(remain)

class Window():

    def __new__(cls) -> Self:

        @dataclass
        class __frames__:
            main: ttk.LabelFrame = None
            main_panel: tk.Frame = None
            main_button: tk.Frame = None
            main_display: tk.Frame = None
            side: ttk.LabelFrame = None

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
            scrollbar: tk.Scrollbar
            scale_apr: ttk.Scale
            scale_year: ttk.Scale
            scale_loan: ttk.Scale
            option_ETP: ttk.Radiobutton
            option_EPP: ttk.Radiobutton
        
        @dataclass
        class __var__:
            mode: tk.StringVar = field(default_factory=tk.StringVar)
            entry_apr: tk.StringVar = field(default_factory=tk.StringVar)
            entry_year: tk.StringVar = field(default_factory=tk.StringVar)
            entry_loan: tk.StringVar = field(default_factory=tk.StringVar)
            scale_apr: tk.DoubleVar = field(default_factory=partial(tk.DoubleVar, value=100))
            scale_year: tk.DoubleVar = field(default_factory=partial(tk.DoubleVar, value=100))
            scale_loan: tk.DoubleVar = field(default_factory=partial(tk.DoubleVar, value=100))

        @dataclass
        class __states__:
            ignore: bool = False
            base_apr: int | float = 0
            base_year: int | float = 0
            base_loan: int | float = 0

        class __const__(Enum):
            text_btn_calc = '計算貸款金額'
            text_btn_clear = '清除'

        class __flash__:
            def __init__(self) -> None: self.slot = None
            def read(self) -> Any: _, self.slot = self.slot, None; return _
            def write(self, __val) -> None: self.slot = __val

        cls.frames = __frames__
        cls.units = __units__
        cls.var = __var__
        cls.states = __states__
        cls.const = __const__
        cls.flash = __flash__
        
        return super().__new__(cls)

    def __init__(self) -> None:

        self.root = tk.Toplevel(root)
        self.root.title('Loan Calculator')
        self.root.iconbitmap('./images/loancalc.ico')
        self.root.geometry(Gadget.getGeometry(self.root, width=960, height=720))
        self.root.option_add('*font', ('Microsoft JhengHei', 10, 'normal'))
        
        self.embed = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)

        self.var = self.var()
        self.states = self.states()
        self.flash = self.flash()
        self.style = ttk.Style()

        self.__init_buildtree__()

    def __init_buildtree__(self) -> Self:

        self.frames = self.frames(
            main = ttk.LabelFrame(self.embed, text='資料輸入區'),
            side = ttk.LabelFrame(self.embed, text='滑桿選擇區')
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
            entry_apr = tk.Entry(self.frames.main_panel, justify=tk.RIGHT, textvariable=self.var.entry_apr),
            entry_year = tk.Entry(self.frames.main_panel, justify=tk.RIGHT, textvariable=self.var.entry_year),
            entry_loan = tk.Entry(self.frames.main_panel, justify=tk.RIGHT, textvariable=self.var.entry_loan),
            label_mpymt_val = tk.Label(self.frames.main_panel, anchor=tk.E),
            label_tpymt_val = tk.Label(self.frames.main_panel, anchor=tk.E),
            btn_calc = ttk.Button(self.frames.main_button, text=self.const.text_btn_calc),
            btn_clear = ttk.Button(self.frames.main_button, text=self.const.text_btn_clear),
            label_panel = tk.Label(self.frames.main_display, anchor=tk.W),
            text_panel = tk.Text(self.frames.main_display, bg=color.white, state=tk.DISABLED),
            scrollbar = tk.Scrollbar(self.frames.main_display),
            scale_apr = ttk.Scale(self.frames.side, from_=200, to=0, orient=tk.VERTICAL, variable=self.var.scale_apr),
            scale_year = ttk.Scale(self.frames.side, from_=200, to=0, orient=tk.VERTICAL, variable=self.var.scale_year),
            scale_loan = ttk.Scale(self.frames.side, from_=200, to=0, orient=tk.VERTICAL, variable=self.var.scale_loan),
            option_ETP = ttk.Radiobutton(self.frames.side, text='本息平均攤還法', value='ETP', variable=self.var.mode, command=self.calc),
            option_EPP = ttk.Radiobutton(self.frames.side, text='本金平均攤還法', value='EPP', variable=self.var.mode, command=self.calc)
        )

        return self.__init_position__()
    
    def __init_position__(self) -> Self:
        
        self.embed.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)
        self.embed.add(self.frames.main, weight=5)
        self.embed.add(self.frames.side, weight=1)
        
        # -------- main ---------

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
        self.units.scrollbar.grid(row=1, column=1, sticky=tk.NSEW)
        self.frames.main_display.grid_rowconfigure(1, weight=1)
        self.frames.main_display.grid_columnconfigure(0, weight=1)

        # -------- side --------

        self.units.scale_apr.grid(row=0, column=0, sticky=tk.NSEW)
        self.units.scale_year.grid(row=0, column=1, sticky=tk.NSEW)
        self.units.scale_loan.grid(row=0, column=2, sticky=tk.NSEW)
        self.units.option_ETP.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
        self.units.option_EPP.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW)

        self.embed.update_idletasks()

        return self.__init_behavior__()
    
    def __init_behavior__(self) -> Self:

        self.units.btn_calc.bind('<Button-1>', self.calc)
        self.units.btn_clear.bind('<Button-1>', self.clear)
        self.units.entry_apr.bind('<FocusIn>', lambda _: partial(self.units.entry_apr.config, fg=color.black, highlightthickness=0))
        self.units.entry_year.bind('<FocusIn>', lambda _: partial(self.units.entry_year.config, fg=color.black, highlightthickness=0))
        self.units.entry_loan.bind('<FocusIn>', lambda _: partial(self.units.entry_loan.config, fg=color.black, highlightthickness=0))
        self.units.scale_apr.bind('<Button-1>', lambda _: self.scaler_guard(self.var.scale_apr.get(), 'apr'))
        self.units.scale_year.bind('<Button-1>', lambda _: self.scaler_guard(self.var.scale_year.get(), 'year'))
        self.units.scale_loan.bind('<Button-1>', lambda _: self.scaler_guard(self.var.scale_loan.get(), 'loan'))
        self.units.scale_apr.bind('<ButtonRelease-1>', lambda _: self.scaler_gate(self.var.scale_apr.get(), 'apr'))
        self.units.scale_year.bind('<ButtonRelease-1>', lambda _: self.scaler_gate(self.var.scale_year.get(), 'year'))
        self.units.scale_loan.bind('<ButtonRelease-1>', lambda _: self.scaler_gate(self.var.scale_loan.get(), 'loan'))
        self.var.entry_apr.trace_add('write', partial(self.scaler_reset, 'apr'))
        self.var.entry_year.trace_add('write', partial(self.scaler_reset, 'year'))
        self.var.entry_loan.trace_add('write', partial(self.scaler_reset, 'loan'))

        return self.__init_adjustment__()
    
    def __init_adjustment__(self) -> Self:

        self.var.mode.set('ETP')
        
        _ = max(len(self.const.text_btn_calc), len(self.const.text_btn_clear))
        self.units.btn_calc.config(text=self.const.text_btn_calc.center(_, '\u3000'))
        self.units.btn_clear.config(text=self.const.text_btn_clear.center(_, '\u3000'))
        
        self.units.label_panel.config(text=linefo('期別', '償還本金', '償還利息', '剩餘本金'))
        self.units.scrollbar.config(command=self.units.text_panel.yview)
        self.units.text_panel.config(yscrollcommand=self.units.scrollbar.set)

        self.embed.update_idletasks()

        return self

    def clear(self, all: bool = True, *args) -> None:
        self.units.text_panel.config(state=tk.NORMAL)
        self.units.text_panel.delete('1.0', tk.END)
        self.units.text_panel.config(state=tk.DISABLED)
        if not all: return
        self.units.entry_apr.delete(0, tk.END)
        self.units.entry_year.delete(0, tk.END)
        self.units.entry_loan.delete(0, tk.END)
        self.units.label_mpymt_val.config(text='')
        self.units.label_tpymt_val.config(text='')
        self.var.scale_apr.set(100)
        self.var.scale_year.set(100)
        self.var.scale_loan.set(100)

    def calc(self, *args) -> None:
        plt.clf()

        try:
            assert is_number(self.var.entry_apr.get()), 'apr' # @IgnoreException
            assert is_integer(self.var.entry_year.get()), 'year' # @IgnoreException
            assert is_number(self.var.entry_loan.get()), 'loan' # @IgnoreException
        
        except AssertionError as _:
            match str(_):
                case 'apr': widget = self.units.entry_apr
                case 'year': widget = self.units.entry_year
                case 'loan': widget = self.units.entry_loan
                
            widget.config(fg=color.crimson, highlightbackground=color.crimson, highlightthickness=1)
            widget.after(1000, partial(widget.config, fg=color.black, highlightthickness=0))            
        
        else:
            value = ntuple('value', ('apr', 'year', 'loan'))(
                apr = float(self.var.entry_apr.get()),
                year = int(self.var.entry_year.get()),
                loan = float(self.var.entry_loan.get())
            )
            rate = ntuple('rate', ('year', 'month'))(year=value.apr/100, month=value.apr/100/12)
            terms = value.year * 12
            balance = value.loan
            monthly = (balance * (1 + rate.month) ** terms * rate.month) / ((1 + rate.month) ** terms - 1)
            self.units.label_mpymt_val.config(text=int(monthly))
            self.units.label_tpymt_val.config(text=int(monthly * terms))
            
            self.clear(all=False)
            self.units.text_panel.config(state=tk.NORMAL)
            
            match self.var.mode.get():
                case 'ETP':
                    dataset = self.calc_ETP(terms, rate.month, monthly, balance)
                case 'EPP':
                    dataset = self.calc_EPP(terms, rate.month, balance)
            
            self.units.text_panel.yview_moveto(1)
            self.units.text_panel.config(state=tk.DISABLED)
            plt.plot(range(1, terms+1), dataset.intst)
            plt.plot(range(1, terms+1), dataset.prin)
            plt.legend(['interest','principal'])
            plt.xlabel("months")
            plt.ylabel("NTD dollars")
            plt.show()

    def calc_ETP(self, terms: int, rate: tuple, monthly: float, balance: float) -> None:
        retval = ntuple('dataset', ('intst', 'prin'))(intst=list(), prin=list())
        for term in range(1, terms + 1):
            interst = rate * balance
            principal = monthly - interst
            balance -= principal
            line = linefo(term, f'{abs(principal):.0f}', f'{abs(interst):.0f}', f'{abs(balance):.0f}')
            self.units.text_panel.insert(tk.END, line + '\n')
            retval.intst.append(interst)
            retval.prin.append(principal)
        
        return retval
    
    def calc_EPP(self, terms: int, rate: tuple, balance: float) -> None:
        retval = ntuple('dataset', ('intst', 'prin'))(intst=list(), prin=list())
        principal = balance / terms
        for term in range(1, terms + 1):
            interst = rate * balance
            balance -= principal
            line = linefo(term, f'{abs(principal):.0f}', f'{abs(interst):.0f}', f'{abs(balance):.0f}')
            self.units.text_panel.insert(tk.END, line + '\n')
            retval.intst.append(interst)
            retval.prin.append(principal)
            
        return retval

    def scaler_guard(self, value: int | float, trigger: Literal['apr', 'year', 'loan'], *args) -> None:
        try:
            self.flash.write(value)
            match trigger:
                case 'apr': assert is_number(self.var.entry_apr.get()) # @IgnoreException
                case 'year': assert is_integer(self.var.entry_year.get()) # @IgnoreException
                case 'loan': assert is_number(self.var.entry_loan.get()) # @IgnoreException
                
        except AssertionError:
            match trigger:
                case 'apr': widget = self.units.entry_apr
                case 'year': widget = self.units.entry_year
                case 'loan': widget = self.units.entry_loan
                
            widget.config(fg=color.crimson, highlightbackground=color.crimson, highlightthickness=1)
            widget.after(1000, partial(widget.config, fg=color.black, highlightthickness=0))
            
        else: self.flash.read()

    def scaler_gate(self, value: int | float, trigger: Literal['apr', 'year', 'loan'], *args) -> None:
        fetch = self.flash.read()
        if fetch is not None:
            match trigger:
                case 'apr': self.var.scale_apr.set(fetch)
                case 'year': self.var.scale_year.set(fetch)
                case 'loan': self.var.scale_loan.set(fetch)
            return
        
        self.states.ignore = True
        match trigger:
            case 'apr':
                entry = self.var.entry_apr
                entry.set(str(apchInt(Gadget.round(str(self.states.base_apr * (value / 100))))))
            case 'year':
                entry = self.var.entry_year
                entry.set(str(int(self.states.base_year * (value / 100))))
            case 'loan':
                entry = self.var.entry_loan
                entry.set(str(apchInt(Gadget.round(str(self.states.base_loan * (value / 100)), '0'))))
        self.states.ignore = False

    def scaler_reset(self, trigger: Literal['apr', 'year', 'loan'], *args) -> None:
        match trigger:
            case 'apr' if is_number(self.var.entry_apr.get()) and not self.states.ignore:
                self.var.scale_apr.set(100)
                self.states.base_apr = float(self.var.entry_apr.get())
            case 'year' if is_integer(self.var.entry_year.get()) and not self.states.ignore:
                self.var.scale_year.set(100)
                self.states.base_year = int(self.var.entry_year.get())
            case 'loan' if is_number(self.var.entry_loan.get()) and not self.states.ignore:
                self.var.scale_loan.set(100)
                self.states.base_loan = float(self.var.entry_loan.get())

window = Window()