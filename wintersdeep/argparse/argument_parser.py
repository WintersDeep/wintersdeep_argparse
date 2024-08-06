# python3 imports
from typing import Any
from collections.abc import Mapping
from argparse import ArgumentParser as NativeArgumentParser, Action

# project imports
from wintersdeep.argparse.mapping_choices_action import MappingChoicesAction
from wintersdeep.argparse.log_level_action import LogLevelAction


## Argument Parser with choices Mapping support.
#  Extension of the native Python3 argparse.ArgumentParser which allows the
#  use of mapping objects in 'choices' and related features.
class ArgumentParser(NativeArgumentParser):

    ## The default short name to use when calling @ref add_log_level_arguments
    DefaultLogLevelShortName = "-l"

    ## The default long name to use when calling @ref add_log_level_arguments
    DefaultLogLevelLongName = "--log-level"

    ## The default help message to show for logging level
    #  @tbd improve this help and add documentation regards available log levels
    DefaultLogLevelHelp = "Configure log levels either globally by setting a log-level alone, or for a specific logger using syntax log-name=log-level."

    ## A list of keyword arguments we need to reject on called to @ref add_log_level_arguments
    LogLevelReservedArguments = [
            'action',
            'nargs',
            'type',
            'choices'
        ]


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


    ## Adds a log level argument to the argument parser.
    #  @remarks all arguments passed to this are identical to those passed
    #    by add_arguments except some may be protected.
    #  @returns the action created by this method call.
    def add_log_level_arguments(self, *name_or_flags:str, **kwargs:dict[str, Any]) -> Action:
        
        name_or_flags = name_or_flags or [ 
            self.DefaultLogLevelShortName,
            self.DefaultLogLevelLongName 
        ]
        
        for reserved_kwarg in self.LogLevelReservedArguments:
            if reserved_kwarg in kwargs:
                raise KeyError(f"Cannot specify {reserved_kwarg} when using add_log_level_arguments.")
        
        kwargs.setdefault("help", self.DefaultLogLevelHelp)
        kwargs['action'] = LogLevelAction
        kwargs['type'] = str

        return self.add_argument(*name_or_flags, **kwargs)