from __future__ import annotations
from dataclasses import dataclass
from collections import namedtuple
from inspect import isclass
from typing import Literal
from ctypes import windll
from decimal import Decimal, ROUND_HALF_UP

def is_number(_) -> bool:
    try: _ = float(_) # @IgnoreException
    except (ValueError, TypeError): return False
    else: return True

def is_integer(_) -> bool:
    try: _ = float(_) # @IgnoreException
    except (ValueError, TypeError): return False
    else: return True if _.is_integer() else False

def apchInt(_) -> int|float:
    return _ if not is_number(_) else int(_) if is_integer(_) else float(_)

class cmdl: ...

cmdl = namedtuple('command_set', ['command', 'value', 'delay'])

class Gadget:
    
    @staticmethod
    def multinput(txt:str, sep:str=None, forceFormat:type=..., autoFormat:bool=True):
        txt = txt.split(sep)
        return (
            tuple(map(forceFormat, txt)) if isclass(forceFormat) else tuple(txt)
        ) if not autoFormat else (
            tuple(map(lambda x: (
                int(x)
                    if is_integer(x) else 
                float(x)
                    if is_number(x) else
                str(x)
            ), txt))
        )
    
    @staticmethod
    def formatter(command:str, split:str=None, strip:str=None) -> cmdl:
        final = list()
        command = command.split(split)
        elem:str
        for elem in command if not isinstance(command, dict) else command.values():
            elem = elem.strip(strip)
            match elem.capitalize():
                case ''|'None': elem = None
                case 'True': elem = True
                case 'False': elem = False
                case _: elem = (
                    int(elem)
                        if is_integer(elem) else
                    float(elem)
                        if is_number(elem) else
                    elem
                )
            final.append(elem)

        while len(final) < 3: final.append(None)
        return cmdl._make(final)
    
    @staticmethod
    def argsplit(cmd:str) -> tuple[str, ...]:
        return tuple([
            value.lower()
                if not is_number(value) else 
            int(value)
                if is_integer(value) else
            float(value)
                for value in cmd.split()
        ])
    
    @staticmethod
    def visualize(ntuple:tuple) -> str:
        """a little gadget for namedtuple, displays its key-name with corresponding value conveniently."""
        return ', '.join(map(lambda key: f'{key} = {getattr(ntuple, key)}', ntuple._fields))
    
    @staticmethod
    def scaler(length: int, reversed: bool = False) -> int:
        ratio = windll.shcore.GetScaleFactorForDevice(0)/100
        return int(length * ratio) if reversed else int(length / ratio)

    @staticmethod
    def getGeometry(window, width: int = 1280, height: int = 720, output: Literal['string', 'metadata'] = 'string') -> str | object:
        
        scaler = __class__.scaler

        ## ------------------------------ ##
        #     1080       864               #
        #   original -> scaled             #
        #   original <- scaled (reversed)  #
        ## ------------------------------ ##
        
        class viewport:
            width = scaler(window.winfo_screenwidth(), reversed=True)
            height = scaler(window.winfo_screenheight(), reversed=True)
        
        match output:
            case 'string':
                return f'{scaler(width)}x{scaler(height)}+{scaler((viewport.width - width)/2)}+{scaler((viewport.height - height)/2)}'
            case 'metadata':
                return namedtuple('metadata', ('width', 'height', 'offset_width', 'offset_height'))(
                    width = scaler(width),
                    height = scaler(height),
                    offset_width = scaler(viewport.width - width)/2,
                    offset_height = scaler(viewport.height - width)/2
                )
            
    @staticmethod
    def round(number: str | int | float, format: str = '.00') -> float:
        return float(Decimal(str(number)).quantize(Decimal(format), ROUND_HALF_UP))

    @staticmethod
    def timeformat(sec: int | float, type: Literal['string', 'set'] = 'string') -> str | tuple:
        hour = int(sec//3600)
        minute = int(sec//60) - (hour * 60)
        second = int(sec) - (minute * 60) - (hour * 3600)

        match type:
            case 'string':
                return f'{hour:0>2d}:{minute:0>2d}:{second:0>2d}' if hour > 0 else f'{minute:0>2d}:{second:0>2d}'
            case 'set':
                return namedtuple('timeformat', ('hr', 'min', 'sec'))(hr=hour, min=minute, sec=second)
            
    @staticmethod
    def parentheless(string: str, sep: str = ',', avoid: str | tuple[str, str] = ('(', ')'), strip: str = None) -> list:
        @dataclass
        class __symbols__:
            enter: str = None
            leave: str = None
            unique: str = None
            
        symbols = __symbols__(*avoid) if len(avoid) > 1 else __symbols__(unique=avoid)
        scopes = list()
        layer = 0
        prev = 0
        for index, char in enumerate(string):
            match char:
                case symbols.enter if len(avoid) > 1: layer += 1
                case symbols.leave if len(avoid) > 1: layer -= 1
                case symbols.unique if len(avoid) <= 1: layer = int(not layer)
                case _ if (char in sep) and (layer == 0): scopes.append(slice(prev, index)); prev = index + 1
        
        scopes.append(slice(prev, None))

        retval = list()
        for scope in scopes: retval.append(string[scope].strip(strip))
        
        return retval