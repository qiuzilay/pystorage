from decimal import Decimal
from modules.toolbox import array, is_number, is_integer, console
from re import findall
from math import radians, sin, cos, tan, log10

class const:
    class regexp:
        init = r'(?:^[\u002B\u002D]?\d*\.?\d+)|(?:\d*\.?\d+)|(?:[A-Za-z]+\u0028)|[^\d\s]'
        digit = r'\d*\.?\d+(?:\^?\d+)*'
        float = r'^(?:[+-]?\d\.\d+)$'
    regex = regexp

def calc(expr:str|array, layer:int=0) -> str:
    _expr = expr.join() if isinstance(expr, array) else expr
    try:

        float(_expr)

    except ValueError: # @IgnoreException

        if not isinstance(expr, array): expr = array(findall(const.regex.init, expr))
        collect = array()
        while expr[0].endswith('\u0028') and expr[-1].__eq__('\u0029'):
            wrapped = False
            bracket = 0
            index = 0
            for index, char in enumerate(expr):
                match char:
                    case _ if char.endswith('\u0028'): bracket += 1
                    case _ if char.endswith('\u0029'): bracket -= 1
                if not bracket: break
            if index.__eq__(expr.length-1):
                wrapped = True
                left, _ = expr.shift(), expr.pop()
                if len(left) > 1: collect.append(left.rstrip('\u0028'))
            if not wrapped: break
        _expr = Expr.extension(Expr.caculate(expr, layer), collect)

    finally:

        if layer:
            return _expr
        else:
            try: final = float(_expr)
            except ValueError: return 'Error'
            else: return str(int(final)) if final.is_integer() else str(final).rstrip('0')
            finally: ...

class Expr:

    @staticmethod
    def caculate(expr:array, layer:int):
        return __class__.arithmetic(__class__.simplify(expr, layer), layer)

    @staticmethod
    def scoper(expr:array, sep:tuple[str], layer:int):
        class Scope:
            def __init__(self, start:int=0, end:int=...):
                self.start = start
                self.end = end
        indices = list()
        count = 0
        pre = 0
        for i, char in enumerate(expr):
            match char:
                case _ if char.endswith('\u0028'):
                    count += 1
                case _ if char.endswith('\u0029'):
                    count -= 1
                case _ if ((char in sep) and not count) and not (char.__eq__('\u002D') and expr[i-1].__eq__('\u005E')):
                    indices.append(Scope(pre, i))
                    pre = i + 1
        
        if len(indices): indices.append(Scope(pre, len(expr)))
        
        scope:Scope
        reduce:int = 0
        for scope in indices:
            _subExpr = expr[scope.start-reduce:scope.end-reduce]
            _calc = calc(_subExpr, layer=layer+1) if _subExpr else '0'
            expr.splice(
                scope.start - reduce,
                scope.end - scope.start,
                _calc
            )
            reduce += scope.end - scope.start - 1
    
    @staticmethod
    def simplify(expr:array, layer:int):
        __class__.scoper(expr, ('\u002B', '\u002D'), layer)
        __class__.scoper(expr, ('\u00D7', '\u002F'), layer)
        __class__.scoper(expr, ('\u005E', '\u0025'), layer)
        __class__.scoper(expr, ('\u221A'), layer)
        return expr

    @staticmethod
    def arithmetic(expr:array, layer:int):
        #console.info(expr)
        nums = array()
        oprs = array()
        for entry in expr:
            try:
                float(entry)
            except ValueError:
                oprs.append(entry)
            else:
                nums.append(Decimal(entry))
            finally: ...
        
        num = next(nums) if not oprs.all(lambda x: x.__eq__('\u221A')) else array(next(nums))
        for opr in oprs:
            _num = next(nums)
            
            match opr:
                case '\u002B':
                    num += _num
                case '\u002D':
                    num -= _num
                case '\u00D7':
                    num *= _num
                case '\u002F':
                    num /= _num
                case '\u005E':
                    ##console.info('num:', num, type(num))
                    ##console.info('_num:', _num, type(_num))
                    ##console.info('result:', num**_num, type(num**_num))
                    num **= _num
                case '\u221A':
                    num.prepend(_num)
                case '\u0025':
                    num *= Decimal('0.01')
                case _:
                    raise Exception('an unexpected error occurred in the arithmetic step.')
        if isinstance(num, array):
            num = num.reduce(lambda x, y: x ** (1/y) if y else x ** Decimal('0.5'))
        return str(int(num)) if float(num).is_integer() else str(num)
    
    @staticmethod
    def extension(expr:str, collection:array) -> str:
        if not is_number(expr): return expr
        else: expr = int(expr) if is_integer(expr) else float(expr)
        for func in collection.reverse():
            match func:
                case 'ABS': return str(abs(expr))
                case 'sin': return str(sin(radians(expr)))
                case 'cos': return str(cos(radians(expr)))
                case 'tan': return str(tan(radians(expr)))
                case 'log': return str(log10(expr))
        return str(expr)