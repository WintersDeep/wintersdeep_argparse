# python3 imports
from typing import Any
from collections.abc import Mapping
from argparse import ArgumentParser as NativeArgumentParser, Action

# project imports
from wintersdeep.argparse.mapping_choices_action import MappingChoicesAction



## Argument Parser with choices Mapping support.
#  Extension of the native Python3 argparse.ArgumentParser which allows the
#  use of mapping objects in 'choices' and related features.
class ArgumentParser(NativeArgumentParser):


    ## Define how a single command-line argument should be parsed.
    #  Same as the native ArgumentParser::add_argument with the following 
    #  exceptions when the 'choices' argument is a Mapping type:
    #    - any 'action' argument will be overwritten with the libraries 
    #      MappingChoicesAction type, the original value will still be honoured
    #      by the MappingChoicesAction action and is passed on in 'next_action'
    #  @see https://docs.python.org/3/library/argparse.html#the-add-argument-method
    #  @param args Either a name or a list of option strings, e.g. foo or -f, --foo.
    #  @param action The basic type of action to be taken when this argument is 
    #      encountered at the command line.
    #  @param nargs The number of command-line arguments that should be consumed.
    #  @param const A constant value required by some action and nargs selections.
    #  @param default The value produced if the argument is absent from the 
    #      command line and if it is absent from the namespace object.
    #  @param type The type to which the command-line argument should be converted.
    #  @param choices A sequence of the allowable values for the argument.
    #  @param required Whether or not the command-line option may be omitted.
    #  @param help A brief description of what the argument does.
    #  @param metavar A name for the argument in usage messages.
    #  @param dest The name of the attribute to be added to the object returned
    #      by parse_args().
    #  @returns The action created from this call.
    def add_argument(self, *args:Any, **kwargs:dict[str, Any]) -> Action:

        choices = kwargs.get('choices', None)

        if choices and isinstance(choices, Mapping):
            kwargs['next_action'] = kwargs.pop('action', None)
            kwargs['action'] = MappingChoicesAction

        return super().add_argument(*args, **kwargs)