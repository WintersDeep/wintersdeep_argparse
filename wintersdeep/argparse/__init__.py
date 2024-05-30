# Package meta data
__summary__ = "Extends the native Python3 `argparse.ArgumentParser` to supports using maps as a `choices` argument type."

__author__      =    "WintersDeep"
__copyright__   =    "Copyright 2020, WintersDeep.com"

__license__     =    "MIT"
__version__     =    "1.0.0"
__credits__     =    [ ]

__maintainer__  =   "WintersDeep.com"
__email__       =   "admin@wintersdeep.com"
__status__      =   "Production"

# project imports
from wintersdeep.argparse.argument_parser import ArgumentParser
from wintersdeep.argparse.mapping_choices_action import MappingChoicesAction

## 'wintersdeep.argparse' module wildcard imports
__all__ = [
    "ArgumentParser",
    "MappingChoicesAction"
]



