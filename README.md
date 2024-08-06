# Wintersdeep Argument Parser

This is a small extension to the native Python3 `argparse.ArgumentParser`. It adds some functionality I find I always end up requiring.

## Installation

```shell
pip install wintersdeep.argparse
```

## Log level support

Often you want the user to be able to configure log levels, thats a pain in itself. Then when you select `debug` and get overwhelmed you realise you only want it on one or more loggers, and not all of them. Often this is done by tweaking the code to acheive what you need in the moment. This helps fix that by making adjusting log levels at the command line simple - take a look:

```python
from wintersdeep.argparse import ArgumentParser

argument_parser = ArgumentParser()
argument_parser.add_log_level_arguments() # there are options here, but the defaults will work fine.
arguments = argument_parser.parse_args()
if log_levels := arguments.log_level:
    log_levels.apply()
```

A user can now type `-l[log-level]` to set the global/default log level, or `-l[logger]=[log-level]` to set a specific log level, or any mix of the two.

```bash
python3 -m path.to.app -lwarning -lpath.to.app.problematic=debug -lpath.to.app.suspect=info
```

## Mapping `choices` support.

It alters the behaviour of the `choices` argument on the `add_argument` method such that it supports the use of `Mapping` objects such as `dict`. 

When using a `Mapping` object as a `choices` constraint the user will be able to choose only from the keys of the `Mapping` object specified. The arguments value in the resulting `Namespace` will be that which is associated with the key in the provided Mapping - e.g. if the user specified the key _"abc"_ the value in the resulting namespace would be taken from `choices_mapping["abc"]`.

As a simple example, the below code accepts any number of integer arguments and prints them to stdout using the CLI specified formatting. The formatter argument `-f` is constrained using `choices` which is provided as the `formatters` `dict` object. Users will only be able to choose one of its keys (`bin`, `hex` or `oct`) and the value in the resulting namespace is the assoicated lambda expression.

```python
from wintersdeep.argparse import ArgumentParser

formatters = {
    "bin": lambda n: f"{n:b}",
    "oct": lambda n: f"{n:o}",
    "hex": lambda n: f"{n:x}"
}

argument_parser = ArgumentParser()
argument_parser.add_argument("N", nargs="+", type=int)
argument_parser.add_argument("-f", choices=formatters, default_key='hex')

arguments = argument_parser.parse_args()

for n in arguments.N:
    print( arguments.formatter(n) )
```

### Features

- Allows usage of `Mapping` type objects as a `choices` constraint on `ArgumentParser::add_argument`. Accepted input will be constrained to key values in the given map and the value in the resulting `Namespace` will be that keys associated value.
- Added a `default_key` keyword argument; you can specify either `default` or `default_key` but not both. When using `default_key` the default value will be the value associated with the specified `default_key` in the `choices` map. `default_key` allows you to ensure documentation and behaviour remain syncronised and readable. `default` can still be used as normal if preferred and is required when the default option should not be user selectable.

## Behaviour Notes

- **The `action` process wasn't applied to the `default` value (specified or derived from `default_key`).**

    This is by intention and is consistent with the native `ArgumentParser` behaviour - the default value is provided _"as-is"_ when the option is not specifed.

- **The `Action` returned by `add_argument` is not the type specified by `add_argument`s `action` parameter**

    The libraries behaviours are implemented by shimming `add_argument`, and inserting a custom `action` when `choices` are a `Mapping` type.

    If you have set your own `action` then `add_argument` will preserve this and invoke it after the value has been translated, so you should still get the expected behaviour. However this does mean the `Action` class return by `add_argument` will not be of the type you originally specified. Your original `action` can be found in the `[action].next_action` property.

    For example, the below script extends the original sample to use an `AddPrefix` action to prefix a string to the user specified formatter. This works identically to the native behaviour, except the `values` argument will be the value from the `choices` mapping.

    ```python
    from argparse import Action
    from wintersdeep.argparse import ArgumentParser

    # A custom action to add a prefix to all formatters.
    class AddPrefix(Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # by the time this action receives `values` it has been converted into its Mapping associated value (in context a lambda function from `formatters`.
            prefix_fn = lambda x: f"Your number is {values(x)}"
            setattr(namespace, self.dest, prefix_fn)

    formatters = {
        "bin": lambda n: f"{n:b}",
        "oct": lambda n: f"{n:o}",
        "hex": lambda n: f"{n:x}"
    }

    argument_parser = ArgumentParser()
    argument_parser.add_argument("N", nargs="+", type=int)
    argument_parser.add_argument("-f", action=AddPrefix, choices=formatters, required=True)

    arguments = argument_parser.parse_args()

    for n in arguments.N:
        print( arguments.formatter(n) )
    
    print(action.__class__.__name__)    # "MappingChoicesAction"
    print(action.next_action.__class__) # <class '__main__.AddPrefix'>
    ```
