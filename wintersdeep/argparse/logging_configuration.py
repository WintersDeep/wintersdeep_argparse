# python3 imports
from logging import INFO, root as root_log, getLogger, basicConfig
from typing import Dict, Optional
from collections import UserDict
 

## Logging level underlying data type.
LogLevel = int

## Map of logger names to their associated log level.
LogLevelMap = Dict[str, LogLevel]



## Represents a logging configuration.
#  This class stores the configuration information about loggers and their
#  associated log level.
class LogLevelConfiguration(UserDict[str, LogLevel]):

    
    ## Creates a new instance of this object.
    #  @param default_level the default level that a logger should emit it.
    #  @param specific_levels map of loggers that have levels specifically set
    #    which usually differ from that defined in @param default_level (but
    #    does not need to).
    def __init__(self, 
                 default_level:Optional[LogLevel]=None,
                 specific_levels:Optional[LogLevelMap]=None) -> None:
        self.default_level:LogLevel = default_level
        super().__init__(specific_levels)


    ## Determines if this object is empty.
    #  @returns bool True when the object contains one or more log level 
    #    definitions, otherwise False.
    def __bool__(self) -> bool:
        return bool(self.data) or not self.default_level is None
    

    ## Updates this logging configuration with data held in anoter.
    #  @note when objects contain conflicting data for any given data point, the
    #    value expressed in @p other is taken as preferred.
    #  @param other the other object to take values from. This can be either be
    #    a @ref dict, in which case only specific log names are updated, or another
    #    @ref LogConfiguration class, in which case both specific and default 
    #    log properties will be updated.
    #  @throws TypeError if @p other is not a supported type to update from.
    def update(self, other:"LogConfiguration") -> None:
        
        if isinstance(other, self.__class__):
            self.default_level = other.default_level
            self.data.update(other.data)

        elif isinstance(other, dict):
            self.data.update(other)

        else:
            raise TypeError("Can only update from other objects of type, or dict.")

    
    ## Applies a logging configuration.
    #  @param args positional arguments passed to native Python3 logging.basicConfig
    #  @param kwargs keyword arguments passed to native Python3 logging.basicConfig
    def apply(self, *args, **kwargs) -> None:
        
        basicConfig(*args, **kwargs)

        if not self.default_level is None:
            root_log.setLevel(self.default_level)

        for log_name, level in self.items():
            logger = getLogger(log_name)
            logger.setLevel(level)


    ## Produces a formal name for this object.
    #  @returns A python string that could be used to reproduce/represent this object.
    def __repr__(self):

        kwargs = {
            "default_level": self.default_level,
            "specific_levels": self.data
        }

        kwargs_strings = [ f"{key}={repr(value)}" for key, value in kwargs.items() ]

        return "{class_name}({ctor_kwargs})".format(
            class_name=self.__class__.__name__,
            ctor_kwargs=", ".join(kwargs_strings)
        )