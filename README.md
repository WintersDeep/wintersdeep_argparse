# Wintersdeep Argument Parser

This is a small extension to the native Python3 `argparse.ArgumentParser`. It alters the behaviour of the `choices` argument on the `add_argument` method such that it supports the use of `Mapping` objects such as `dict`. 

When using a `Mapping` object as a `choices` constraint the user will be able to choose only from the keys of the `Mapping` object specified. The arguments value in the resulting `Namespace` will be that which is associated with the key in the provided Mapping - e.g. if the user specified the key _"abc"_ the value would be taken from `Mapping["abc"]`.

In such cases 

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

## Installation

```shell
pip install wintersdeep.argparse
```

## Features

- Allows usage of `Mapping` type objects as a `choices` constraint on `ArgumentParser::add_argument`. Accepted input will be constrained to key values in the given map and the value in the resulting `Namespace` will be that keys associated value.
- Added a `default_key` keyword argument; you can specify either `default` or `default_key` but not both. When using `default_key` the default value will be the value associated with the specified `default_key` in the `choices` map. `default_key` allows you to ensure documentation and behaviour remain syncronised and readable. `default` can still be used as normal if preferred, and is required when the default option is not user selectable.

## Behaviour Notes

- **The `action` wasn't applied to the `default` value (specified or derived from `default_key`).**

    This is by intention and is consistent with the native `ArgumentParser` behaviour - the default value is provided _"as-is"_ when the option is not specifed.

- **The `Action` returned by `add_argument` is not the type specified**

    The libraries behaviours are implemented by shimming `add_argument`, and inserting a custom `action` when `choices` are a `Mapping` type.

    If you have set your own `action` then `add_argument` will preserve this and invoke it after the value has been translated, so you should still get the expected behaviour. However this does mean the `Action` class return by `add_argument` will not be of the type you originally specified. Your original `action` can be found in the `[action].next_action` property.

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
    argument_parser.add_argument("-f", choices=formatters, default_key='hex')

    arguments = argument_parser.parse_args()

    for n in arguments.N:
        print( arguments.formatter(n) )
    
    print(action.__class__.__name__)    # "MappingChoicesAction"
    print(action.next_action.__class__) # <class '__main__.AddPrefix'>
    ```