from inspect import isclass
from ctypes import windll

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

class Gadget:

    @staticmethod
    def setGeometry(width:int=1280, height:int=720, window=...) -> str:

        ratio = windll.shcore.GetScaleFactorForDevice(0)/100

        ## ------------------------------ ##
        #     1080       864               #
        #   original -> scaled             #
        #   original <- scaled (reversed)  #
        ## ------------------------------ ##

        def scaler(length:int, reversed=False):
            nonlocal ratio
            return int(length * ratio) if reversed else int(length / ratio)
        
        class viewport:
            width = scaler(window.winfo_screenwidth(), reversed=True)
            height = scaler(window.winfo_screenheight(), reversed=True)

        return f'{scaler(width)}x{scaler(height)}+{scaler((viewport.width - width)/2)}+{scaler((viewport.height - height)/2)}'