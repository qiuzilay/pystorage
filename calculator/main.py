from modules.calculator import calc, array
from modules.toolbox import Gadget, is_number, console
from functools import partial
from typing import Literal, Callable
from re import match, search, findall
from os import chdir
from os.path import dirname, realpath
from sys import exc_info
import tkinter as Tkinter
import json

chdir(dirname(realpath(__file__)))

BLANK = ''

class window: ...
class keyframe: ...
class textframe: ...
class textfield: ...
class constants:
    class regexp:
        init = r'(?:^[\u002B\u002D]?\d*\.?\d+)|(?:\d*\.?\d+)|(?:[A-Za-z]+\u0028)|[^\d\s]'
        any = r'(?:(?:\d*\.?\d+)|[^\d\s]|^)$'
        symbol = r'[\u002B\u002D\u00D7\u002F\u005E\u0025\u0028\u0029\u221A]$'
        numeric = r'(?:\d*\.?\d+)$'
        float = r'(?:\d*\.+?\d+)$'
        operator = r'[\u002B\u002D\u00D7\u002F]$'
    regex = regexp

class Button(Tkinter.Button):

    def __init__(self, master=None, command:Callable=..., compound:str=..., cursor:str=..., default:Literal['normal', 'active', 'disabled']=..., font:str=..., height=..., image:str=..., justify:Literal['left', 'center', 'right']=..., name:str=..., padx=..., pady=..., relief=..., repeatdelay:int=..., repeatinterval:int=..., text:float|str=..., width:int=..., bg:str='white', fg:str='black', border:int=2, focusbg:str='#F0F0F0'):
        self.__image:Tkinter.PhotoImage = image
        super().__init__(master=master, text=text, image=self.__image, width=width, height=height, bg=bg, fg=fg, border=border, relief=relief, compound=compound, activebackground=focusbg, command=command, font=font)

def trigger(chr:str) -> None:
    #textfield.xview_moveto(1)
    (
        entry.text.reset()
            if entry.text.value in ('Error', BLANK) else
        entry.text.set(entry.textfield.get())
            if entry.textfield.get().__ne__(entry.text.value) else
        ...
    )

    match chr:
        case 'AC':
            entry.text.reset()
        case '\u232B': # "⌫"
            entry.text.remove()
        case '\u00B1': # "±"
            entry.text.reverse()
        case '\u003D': # "="
            if not search(r'(?:\d+$)|\u0029$', entry.text.value):
                entry.text.value += '0'
            #console.info('text.value:', entry.text.value)
            #console.info('textfield:', entry.textfield.get())
            entry.text.set(calc(entry.text.value))
        case _:
            entry.text.add(chr)

def update(*args, **kwargs):
    entry.text.value = entry.textfield.get()
    console.log(entry.text.value, end='\r')

def sync(cursor:Literal['normal', 'end']='normal'):
    def inner(func:Callable):
        def wrapper(*args, **kwargs):

            _diff = len(entry.text.value)
            _cursor = textfield.index(Tkinter.INSERT)

            console.log(' ' * len(entry.text.value), end='\r')
            
            func(*args, **kwargs)
            
            entry.textfield.set(entry.text.value)
            match cursor.lower():
                case 'end':
                    textfield.icursor(len(entry.text.value))
                case _:
                    entry.textfield.set(entry.text.value)
                    _diff = len(entry.text.value) - _diff
                    textfield.icursor(_cursor + _diff if entry.text.value != '0' else 1) if _diff else ...

            return console.log(entry.text.value, end='\r')
        return wrapper
    return inner

class Entry:
    
    class text_prototype:
        value = '0'

        @staticmethod
        @sync()
        def add(chr:str) -> str:
            text = __class__
            if match(r'[0-9]', chr):
                (
                    text.insert(chr)
                        if text.endswith('nonzero') else
                    text.replace(chr)
                        if chr.__ne__('0') else
                    ...
                )
            else:
                match chr:
                    case ('\u002B'|'\u002D'|'\u00D7'|'\u002F'): # ( + | - | × | / )
                        (   
                            ...
                                if
                                    (text.endswith('\u0028') and chr.__ne__('\u002D'))
                                        or
                                    (text.endswith('\u0028\u002D') and chr.__ne__('\u002B'))                                 
                                else
                            text.remove() # chr at here absolutely is "+", and text.value absolutey endswith "-".
                                if text.endswith('\u0028\u002D') else
                            text.insert('0' + chr)
                                if text.endswith('\u002E') else
                            text.replace(chr)
                                if text.endswith('operator') else
                            text.insert(chr)
                        )
                    case '\u002E': # "."
                        (
                            text.insert('0' + chr)
                                if text.endswith('operator') else
                            text.insert(chr)
                                if not text.endswith('float') else
                            ...
                        )
                    case '\u005E': # "^"
                        (
                            text.insert(chr)
                                if text.endswith('numeric', incl='\u0029') else
                            ...
                        )
                    case '\u0025': # "%"
                        (
                            text.insert(chr)
                                if text.endswith('numeric', incl=('\u0029', '\u0025')) else
                            ...
                        )
                    case '\u0028': # "("
                        (
                            text.replace(chr)
                                if text.value.__eq__('0') else
                            text.insert('\u00D7' + chr)
                                if text.endswith('numeric', incl=('\u0025', '\u0029')) else
                            text.insert(chr)
                                if text.endswith('operator', incl=('\u005E', '\u221A', '\u0028')) else
                            text.insert('0' + chr)
                                if text.endswith('\u002E') else
                                ...
                        )
                    case '\u0029': # ")"
                        if (not text.endswith('operator', incl=('\u005E', '\u221A', '\u0028'))):
                            text.insert(chr)
                    case '\u221A': # "√"
                        (
                            text.insert(chr)
                                if text.endswith('nonzero') else
                            text.replace(chr)
                        )
                    case '\u207B': # "⁻" (Multi-Inverse)
                        (
                            text.insert('\u005E-1')
                                if text.endswith('numeric', incl='\u0029') else
                            ...
                        )
                    case 'ABS': # absolute
                        text.wrap('ABS')
                    case 'sin':
                        text.wrap('sin')
                    case 'cos':
                        text.wrap('cos')
                    case 'tan':
                        text.wrap('tan')
                    case 'log':
                        text.wrap('log')
                    case _:
                        raise Exception('invalid character was detected.')
            return text.value
        
        @staticmethod
        @sync()
        def remove() -> str:
            text = __class__
            pos = textfield.index(Tkinter.INSERT)
            if text.value.__ne__('0') and pos:
                if len(text.value) > 1:
                    text.value = text.value[:pos-1] + text.value[pos:]
                else:
                    text.value = '0'
            return text.value
        
        @staticmethod
        @sync(cursor='end')
        def set(string:str) -> str:
            text = __class__
            text.value = string
            return text.value
        
        @staticmethod
        @sync(cursor='end')
        def reset() -> str:
            text = __class__
            text.value = '0'
            return text.value

        @staticmethod
        @sync()
        def reverse() -> str:
            text = __class__
            pos = textfield.index(Tkinter.INSERT)
            ahead = search(r'\d*\.?\d+$', text.value[:pos])
            behind = search(r'^\d*\.?\d+', text.value[pos:])
            class scope_prototype:
                start = (
                    None
                        if ((ahead is None) and (behind is None)) else
                    ahead.start()
                        if (ahead is not None) else
                    behind.start() + pos
                )
                end = (
                    None
                        if ((ahead is None) and (behind is None)) else
                    behind.end() + pos
                        if (behind is not None) else
                    ahead.end()
                )
            scope = scope_prototype
            
            if None not in (scope.start, scope.end):
                
                #console.info(f'{text.value[scope.start:scope.end]} [{scope.start}:{scope.end}]')

                match text.value[scope.start-1] if scope.start > 0 else BLANK:
                    case '+':
                        text.value = text.value[:scope.start-1] + '-' + text.value[scope.start:]
                    case '-':
                        if match(r'\([-]\d*\.?\d+\)', text.value[scope.start-2:scope.end+1]): # -123+(-4567) -> 123+4567
                            text.value = text.value[:scope.start-2] + text.value[scope.start:scope.end] + text.value[scope.end+1:]
                        else:
                            if scope.start > 1: # -123-4567 -> -123+4567
                                text.value = text.value[:scope.start-1] + '+' + text.value[scope.start:]
                            else: # -123-4567 -> 123-4567
                                text.value = text.value[scope.start:]
                    case '': # 123-4567 -> -123-4567
                        text.value = '-' + text.value[scope.start:]
                    case _:
                        text.value = text.value[:scope.start] + f'(-{text.value[scope.start:scope.end]})' + text.value[scope.end:]

            return text.value

        @classmethod
        def insert(text, chr:str) -> str:
            pos = textfield.index(Tkinter.INSERT)
            text.value = text.value[:pos] + chr + text.value[pos:]
            return text.value
        
        @classmethod
        def replace(text, chr:str) -> str:
            pos = textfield.index(Tkinter.INSERT)
            text.value = text.value[:pos-1] + chr + text.value[pos:]
            return text.value

        @classmethod
        def endswith(text, type:Literal['nonzero', 'numeric', 'operator', 'float', 'symbol']='nonzero', incl:tuple[str]|str=...) -> bool:
            trunc = text.value[:textfield.index(Tkinter.INSERT)]
            judge = (
                search(const.regex.any, trunc).group().__ne__('0')
                    if (type.lower().__eq__('nonzero')) else
                search(const.regex.numeric, trunc) is not None
                    if (type.lower().__eq__('numeric')) else
                search(const.regex.operator, trunc) is not None
                    if (type.lower().__eq__('operator')) else
                search(const.regex.float, trunc) is  not None
                    if (type.lower().__eq__('float')) else
                search(const.regex.symbol, trunc) is not None
                    if (type.lower().__eq__('symbol')) else
                trunc.endswith(type)
            )
            return (judge) if (incl is Ellipsis) else (judge or trunc.endswith(incl))
       
        @classmethod
        def wrap(text, name:Literal['ABS', 'sin', 'cos', 'tan', 'log']):

            def pointer() -> int:
                nonlocal expr, pos
                trunc = array(findall(const.regex.init, text.value[:pos]))
                return expr.length - (expr - trunc).length + (trunc - expr).length - 1
            
            class element(str):
                def __init__(self, _):
                    super().__init__()
                    self.index = None
                    
                @property
                def index(self) -> int: return self.__index

                @index.setter
                def index(self, _:int): self.__index = _

                @property
                def group(self) -> Literal['protect', 'bracket', 'numeric', 'symbol', 'undefined']:
                    return (
                        'protect'
                            if self in ('-', '%', '√') else
                        'bracket'
                            if self.endswith(('\u0028', '\u0029')) else
                        'numeric'
                            if is_number(self) else
                        'symbol'
                            if self else
                        'undefined'
                    )
                
            def frame(index:int) -> tuple[element, element, element]:
                nonlocal expr
                cap = expr.length
                i = 0 if (index < 0) else index if (index < cap) else cap - 1
                obj_self, obj_prev, obj_next = (
                    (element(expr[i])),
                    (element(expr[i-1]) if i > 0 else None),
                    (element(expr[i+1]) if i < cap - 1 else None)
                )
                obj_self.index = i
                if obj_prev is not None: obj_prev.index = i-1
                if obj_next is not None: obj_next.index = i+1
                return (obj_self, obj_prev, obj_next)
            
            
            pos = textfield.index(Tkinter.INSERT)
            expr = array(findall(const.regex.init, text.value))
            self, prev, next = frame(pointer())
            
            class scope:
                start = self.index
                end = self.index + 1

            def skiper(elem:element, lookahead:bool=False) -> int:
                bracket = 0
                while True:
                    match elem:
                        case _ if elem.endswith('\u0028'):
                            bracket += 1
                        case _ if elem.endswith('\u0029'):
                            bracket -= 1
                    elem = frame(elem.index)[2 if not lookahead else 1]
                    if not bracket: break
                return (elem.index if not lookahead else elem.index+1) if elem is not None else (expr.length if not lookahead else 0)
            
            if prev is not None:
                if is_number(self):
                    match prev.group:
                        case 'protect' if frame(prev.index)[1].group != 'numeric': scope.start = prev.index # 前面是受保護的符號，再更前面如果仍不是數字，儲存此符號的位置
                        #case 'bracket': assert prev == ')', "right parentheses shouldn't be followed by a numeric"
                        #case 'numeric': raise AssertionError("numeric be followed by another numeric is impossible")
                        case _: ...
                elif self.group != 'bracket': # 非數字非括號之符號
                    match prev.group:
                        case 'numeric' if next.group == 'bracket': # 3'-'(...)
                            scope.start += 1
                            scope.end = skiper(next)
                        case 'numeric': # 自身是符號，前方是數字
                            match self:
                                case '%': scope.start = prev.index
                                case _: scope.start += 1; scope.end += 1
                        case _: # 自身是符號，但前方仍是符號
                            match self:
                                case '%': scope.start = skiper(prev, lookahead=True) # 3×(32767-1024)%
                                case _:
                                    scope.start += 1 if prev == '\u0029' else 0
                                    scope.end = skiper(next, lookahead=False)
                else: # 括號另外處理
                    match self:
                        case _ if self.endswith('\u0028'):
                            match next.group:
                                case 'numeric': scope.start += 1; scope.end += 1
                                case 'protect': scope.start += 1; scope.end = skiper(frame(next.index)[2], lookahead=False)
                                case _: scope.start += 1; scope.end = skiper(next, lookahead=False) + 1
                        case _ if self.endswith('\u0029'):
                            scope.start = skiper(self, lookahead=True)
                            scope.end += 1 if next == '%' else 0
            elif pos:
                match self.group:
                    case _ if self.endswith('\u0028'):
                        match next.group:
                            case 'numeric': scope.start += 1; scope.end += 1
                            case 'protect': scope.start += 1; scope.end = skiper(frame(next.index)[2], lookahead=False)
                            case _: scope.start += 1; scope.end = skiper(next, lookahead=False) + 1
                    case 'numeric': ...
            else:
                match self.group:
                    case _ if self.endswith('\u0028'): scope.end = skiper(self, lookahead=False)
                    case 'protect' if next.group == 'bracket': scope.end = skiper(next, lookahead=False)
                    case 'protect' if next.group == 'protect': scope.end = skiper(frame(next.index)[2], lookahead=False)
                    case 'protect' if next.group == 'numeric': scope.end += 1

            expr = expr.splice(scope.start, scope.end-scope.start, f'{name}({expr[scope.start:scope.end].join()})').join()
            text.value = expr
            return expr

    text = text_prototype
    textfield:Tkinter.StringVar = None

entry = Entry
const = constants
window = Tkinter.Tk(className='main')
keyframe = Tkinter.Frame(window)
textframe = Tkinter.Frame(window, bg='white')
entry.textfield = Tkinter.StringVar()
entry.textfield.trace_add('write', update)
textfield = Tkinter.Entry(
    master = textframe,
    bd = 0,
    relief = Tkinter.FLAT,
    justify = Tkinter.RIGHT,
    font = ('Microsoft JhengHei', 32, 'bold'),
    textvariable = entry.textfield
)

window.title('The Caculator')
window.geometry(Gadget.setGeometry(window=window, width=720, height=560))
window.resizable(True, True)
window.iconbitmap('./icon.ico')
window.option_add('*font', ('Microsoft JhengHei', 16, 'normal'))

textframe.grid(sticky=Tkinter.NSEW)
textfield.grid(sticky=Tkinter.NSEW, padx=12)
keyframe.grid(sticky=Tkinter.NSEW)

with open('./buttons.json', mode='r', encoding='UTF-8') as _cfg:
    for name, cfg in json.load(_cfg).items():

        Button(
            master = keyframe,
            width = 0,
            height =  0,
            border = 1,
            relief = Tkinter.FLAT,
            compound = Tkinter.CENTER,
            bg = cfg['bgcolor'],
            fg = cfg['fgcolor'],
            focusbg = cfg['bgfocus'],
            font = (
                cfg.get('font', {"family": "Microsoft JhengHei"})['family'],
                cfg.get('font', {"size": 16})['size'],
                cfg.get('font', {"weight": "normal"})['weight']
            ),
            command = partial(trigger, cfg['value']),
            text = name if not name.endswith('.png') else BLANK,
            image = (
                Tkinter.PhotoImage() if not name.endswith('.png') else
                Tkinter.PhotoImage(file=name).subsample(12)
            )
        ).grid(
            row = cfg['row'], 
            column = cfg['column'], 
            columnspan = cfg.get('colspan', 1), 
            sticky = Tkinter.NSEW
        )

window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=3)
window.columnconfigure(0, weight=1)

textframe.rowconfigure(0, weight=1)
textframe.columnconfigure(0, weight=1)

cols, rows = keyframe.grid_size()
for row in range(rows): keyframe.rowconfigure(row, weight=1)
for col in range(cols): keyframe.columnconfigure(col, weight=1)

entry.text.set('0')

window.mainloop()