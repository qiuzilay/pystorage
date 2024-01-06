from typing import Literal, Self, get_args, Any
from inspect import getframeinfo, stack
from traceback import format_stack
from collections import namedtuple as ntuple
from dataclasses import asdict, is_dataclass
from threading import Thread
from queue import Queue
from enum import Enum, EnumType
from re import search


class Console:

    def __new__(cls, *args, **kwargs) -> Self:
        
        class __awaited__:
            def __init__(self, *args, **kwargs) -> None:
                self.args = args
                self.kwargs = kwargs
        
        class __const__(Enum):
            def __get__(self, object: None, cls: EnumType) -> Any:
                return self.value
            blackslash = '\u005C'
            whitespace = '\u0020'
            tab = '    '
            l_bracket = '\u007B'
            r_bracket = '\u007D'
        
        cls.awaited = __awaited__
        cls.const = __const__

        return super().__new__(cls)

    def __init__(self) -> None:
        self.__mode__ = 'debug'
        self.__queue__ = Queue()
        Thread(target=self.__printer__, name='toolbox.console', daemon=True).start()
    
    @property
    def mode(self) -> Literal['normal', 'debug']:
        return self.__mode__
    
    @mode.setter
    def mode(self, value: Literal['normal', 'debug']):
        if value in get_args(Literal['normal', 'debug']):
            self.__mode__ = value

    def __printer__(self):
        while True:
            package: __class__.awaited = self.__queue__.get()
            print(*package.args, **package.kwargs)

    def log(self,
            *text: str,
            sep: str = ' ',
            end: str = '\n',
            mode: Literal['normal', 'debug'] = 'normal') -> str:
        
        final = sep.join(map(str, text))

        if (mode != 'debug') or (self.mode == 'debug'):
            self.__queue__.put_nowait(self.awaited(final, end=end))
        
        return final
    
    def info(self,
            *text: str,
            sep: str = ' ',
            end: str = '\n',
            mode: Literal['normal', 'debug'] = 'normal') -> tuple[str, str]:
        
        upper = getframeinfo(stack()[1][0])
        prefix = f'<{upper.filename.split(self.const.blackslash)[-1]}:{upper.lineno}>'
        final = sep.join(map(str, text))

        if (mode != 'debug') or (self.mode == 'debug'):
            self.__queue__.put_nowait(self.awaited(prefix, final, end=end))
        
        return ntuple('callback', ('prefix', 'content'))(prefix=prefix, content=final)
    
    def debug(self,
            object: Any,
            end: str = '\n',
            mode: Literal['normal', 'debug'] = 'normal') -> Any:
        
        def parentheless(string: str,
                        sep: str | tuple[str, ...] = ',',
                        symbols: tuple[str, str] = ('(', ')'),
                        strip: str = None):
            class symbols:
                nonlocal sep, symbols
                enter, leave = symbols
            scopes = list()
            layer = 0
            prev = 0
            for index, char in enumerate(string):
                match char:
                    case symbols.enter: layer += 1
                    case symbols.leave: layer -= 1
                    case _ if (char in sep) and (layer == 0): scopes.append(slice(prev, index)); prev = index + 1
            
            scopes.append(slice(prev, None))

            retval = list()
            for scope in scopes: retval.append(string[scope].strip(strip))
            
            return retval
        
        varname = None
        name = f'{self.__class__.__name__.lower()}.{stack()[0][3]}'
        for line in reversed(format_stack()):
            if name in line:
                for elem in parentheless(', '.join(map(lambda _: _.strip(), line.splitlines()))):
                    if name in elem:
                        regex = r'(?<=' + r'\.'.join(name.split('.')) + r'\()[A-Z_a-z0-9]+(?=\))'
                        varname = search(regex, elem)
                        break
        if varname is not None: varname = varname.group()

        upper = getframeinfo(stack()[1][0])
        prefix = f'<{upper.filename.split(self.const.blackslash)[-1]}:{upper.lineno}>'

        if (mode != 'debug') or (self.mode == 'debug'):
            if not is_dataclass(object) or not is_dataclass(type(object)):
                self.__queue__.put_nowait(
                    self.awaited(
                        prefix, f'{varname}: {object}' if varname else object, type(object), end=end
                    )
                )
            else:
                elems = asdict(object)
                self.__queue__.put_nowait(
                    self.awaited(
                        f'{prefix} {self.const.l_bracket}',
                        ',\n'.join(map(
                            lambda key:
                            self.const.tab + f'{key} = {elems.get(key)} {type(elems.get(key))}',
                            elems
                        )),
                        f"{self.const.r_bracket} [dataclass '{varname}']", sep='\n', end=end
                    )
                )
        
        return object
        

#class Console_deprecated:
#
#    BACKSLASH = '\u005C'
#    mode:Literal['normal', 'debug'] = 'debug'
#
#    @classmethod
#    def load(cls, func:FunctionType, *text:str, sep=' ', end='\n', dots:int=4, repeat:int=0, mode:Literal['debug']=...):
#        cal = getframeinfo(stack()[1][0])
#        cbf:str = None
#        length:int = 0
#        if mode.__ne__('debug') or cls.mode.__eq__('debug'):
#            for loop in range(repeat+1):
#                if not loop:
#                    cbf = func(*text, sep=sep, end='', caller=cal)
#                    length = len(' '.join(cbf).encode())                    
#                else:
#                    sleep(1)
#                    print('\r' + ' ' * (length + dots), end='\r')
#                    func(*text, sep=sep, end='', caller=cal)
#
#                for i in range(dots):
#                    sleep(1)
#                    print('.', end='' if (loop < repeat or i+1 < dots) else end, flush=True)
#        else:
#            cbf = func(*text, sep=sep, end='', caller=cal, mode=mode)
#        
#        return cbf.result if isinstance(cbf, tuple) else cbf
#
#    @classmethod
#    def log(cls, *text:str, sep=' ', end='\n', caller:Traceback=..., mode:Literal['debug']=...) -> str:
#        result = sep.join(map(str, text))
#        print(result, end=end) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
#        
#        return result
#
#    @classmethod
#    def info(cls, *text:str, sep=' ', end='\n', caller:Traceback=..., mode:Literal['debug']=...) -> str:
#        cal = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
#        result = sep.join(map(str, text))
#        prefix = f'<{cal.filename.split(cls.BACKSLASH)[-1]}:{cal.lineno}>'
#        print(prefix, result, end=end) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
#        
#        return (
#            result
#                if not isinstance(caller, Traceback) else 
#            ntuple('callback', ('result', 'prefix'))(result=result, prefix=prefix)
#        )
#    
#    @classmethod
#    def debug(cls, obj:object, end='\n', caller:Traceback=..., mode:Literal['debug']=...):
#
#        def parentheless(string:str, sep:str|tuple[str, ...]=',', symbols:tuple[str, str]=('(', ')'), strip:str=None):
#            class symbols:
#                nonlocal sep, symbols
#                enter, leave = symbols
#            flags = list()
#            layer = 0
#            prev = 0
#            for index, char in enumerate(string):
#                match char:
#                    case symbols.enter: layer += 1
#                    case symbols.leave: layer -= 1
#                    case _ if (char in sep) and (layer == 0): flags.append(slice(prev, index)); prev = index + 1
#            
#            flags.append(slice(prev, None))
#
#            retval = list()
#            for scope in flags: retval.append(string[scope].strip(strip))
#            
#            return retval
#
#        varname = None
#        name = f'{cls.__name__.lower()}.{stack()[0][3]}'
#        for line in reversed(format_stack()):
#            if name in line:
#                for elem in parentheless(', '.join(map(lambda _: _.strip(), line.splitlines()))):
#                    if name in elem:
#                        regex = r'(?<=' + r'\.'.join(name.split('.')) + r'\()[A-Z_a-z0-9]+(?=\))'
#                        varname = search(regex, elem)
#                        break
#
#        cal = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
#        print(
#            f'<{cal.filename.split(cls.BACKSLASH)[-1]}:{cal.lineno}>',
#            f'{varname.group()}: {obj}' if varname is not None else obj, type(obj),
#            end=end
#        ) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
#        
#        return obj
#
#    @classmethod
#    def viewer(cls, clsname: str = 'dataclass', obj: Literal['<instance dataclass>'] = None, sep='\n', end='\n', caller: Traceback = ..., mode: Literal['debug'] = ...) -> Literal['<object metadata>']:
#        cal = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
#        if obj is not None:
#            attr = asdict(obj)
#            print(
#                f'<{cal.filename.split(cls.BACKSLASH)[-1]}:{cal.lineno}> (',
#                *map(lambda key: '\t'f'{key}: {attr.get(key)}', attr),
#                f') <instance {clsname}>', sep=sep, end=end
#            ) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
#        else:
#            print(obj, type(obj), end=end) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
#
#        return obj
#
#console = Console()