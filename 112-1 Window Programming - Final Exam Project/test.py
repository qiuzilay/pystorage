from os import chdir, getcwd
from os.path import dirname, realpath
from time import sleep
from sys import modules

chdir(dirname(realpath(__file__)))

from modules.toolbox import array, slider, console
from modules.toolbox.interface import terminal, input

terminal.create(daemon=False)

get = input('fan is: ')

console.info(get)

get = input('cat is not: ')

console.info(get)