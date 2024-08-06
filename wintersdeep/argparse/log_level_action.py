# python3 imports
from argparse import Action
from typing import Any, Mapping
from argparse import ArgumentParser, Namespace, ArgumentError
from logging import (
    CRITICAL,
    ERROR,
    WARNING,
    INFO,
    DEBUG,
    NOTSET,
 )

# project imports
from wintersdeep.argparse.logging_configuration import LogLevelConfiguration, LogLevel



## Log level action
#  Handles converting a user supplied value into a logging configuration
#  object which can be added to the arguments namespace. Log levels can be
#  provided as either strings (see @ref LogLevelAction.LogLevelStrings below) or
#  positive numerical constants (as parsed by `int(x, 0)`). Log levels strings 
#  can take two forms, either "[log-level]" whereby the default/global log level
#  is set, or "[logger-name]=[log-level]" in which case the log level for that
#  specific logger (and any underneath it) will be assigned.
class LogLevelAction(Action):

    
    ## The list of log-level strings we accept and their associated severity.
    LogLevelStrings = {
        "critical": CRITICAL,
        "fatal": CRITICAL,
        "error": ERROR,
        "warn": WARNING,
        "warning": WARNING,
        "information": INFO,
        "info": INFO,
        "debug": DEBUG,
        "verbose": DEBUG,
        "unset": NOTSET,
    }

    ## Adds or updates the @p namespace with the contents of @p log_levels.
    #  @note either sets namespace.dest to @p log_levels, unless the log levels
    #    are already set, in which case updates the log levels that are in place.
    #  @param namespace the namespace to add log level data to.
    #  @param log_levels the log levels to add to the namespace.
    def apply_or_update(self, namespace:Namespace, log_levels:LogLevelConfiguration) -> None:
        if existing_log_levels := getattr(namespace, self.dest, self.default):
            existing_log_levels.update(log_levels)
        else:
            setattr(namespace, self.dest, log_levels)
    
    ## Parse a log level string into a log level numerical constant.
    #  @param log_level_string the string received from the CLI.
    #  @returns the numerical value of the log level parsed.
    #  @throws ValueError if a numerical interpretation of the @p log_level_string
    #    cannot be determined.
    @classmethod
    def parse_log_level(cls, log_level_string:str) -> LogLevel:

        log_level = None
        try: # to parse the value as an in
            log_level = int(log_level_string, 0)
        except ValueError: # whereby assume its a written string.
            log_level = cls.LogLevelStrings.get(
                log_level_string.lower(), None
            )
        
        if log_level is None or log_level < 0:
            raise ValueError(f"'{log_level_string}' does not appear to be a valid log level string.")

        return log_level



    ## Used to convert the CLI argument into its associated log configuration.
    #  @param parser The ArgumentParser object which contains this action.
    #  @param namespace The Namespace object that will be returned by parse_args().
    #  @param values The associated command-line arguments, with any type conversions applied.
    #  @param option_string The option string that was used to invoke this action.
    def __call__(self, parser, namespace, values, option_string=None):
        
        # we build from the default as any CLI specified values may not envelope
        # all default values provided.
        log_levels = self.default or LogLevelConfiguration()

        if isinstance(values, str):
            values = [ values ]

        if not isinstance(values, list):
            raise ValueError("'value' argument must be of `str` or `list` type.")
        
        try:

            for log_level_argument in values:

                log_level_argument_parts = log_level_argument.rsplit(r"=", maxsplit=1)
                
                if len(log_level_argument_parts) == 1: # global assignment
                    log_level = self.parse_log_level(log_level_argument_parts[0])
                    log_levels.default_level = log_level

                else: # len(log_level_argument_parts) > 1 - specific assignment 
                    log_name, log_level_string = log_level_argument_parts
                    log_level = self.parse_log_level(log_level_string)
                    log_levels[log_name] = log_level

        except ValueError as ex:

            raise ArgumentError(self, str(ex)) from ex

        self.apply_or_update(namespace, log_levels)