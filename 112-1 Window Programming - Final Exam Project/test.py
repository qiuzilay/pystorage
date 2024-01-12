from os import chdir
from os.path import dirname, realpath

chdir(dirname(realpath(__file__)))

from modules.toolbox import  console, is_number
from modules.toolbox.interface import terminal, input
from dataclasses import dataclass, field
from typing import Self

terminal.create()

class tester:
    def __new__(cls, *args, **kwargs) -> Self:
        
        @dataclass
        class __vars__:
            const: list = field(default_factory=list)
        
        cls.vars = __vars__()
        
        return super().__new__(cls)

    def __init__(self, value) -> None:
        self.vars.const.append(value)
        
tester1 = tester('1')
tester2 = tester('2')

console.info(tester1.vars.const, id(tester1.vars.const))
console.info(tester2.vars.const, id(tester2.vars.const))

console.info(input('owo: '))
console.info(input('老師新年快樂: '))