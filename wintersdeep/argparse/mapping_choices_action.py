# python3 imports
from argparse import Action
from typing import Any, Mapping



## Mapping choices action
#  Handles converting a user supplied value its associated value using the 
#  choices map. This action will replace an user configured 'action' value
#  provided to `add_argument`, but it will pass on its translated value to
#  the one that was originall defined.
class MappingChoicesAction(Action):


    ## Initialises a new instance of this object.
    #  @param args positional arguments provided to the initialiser.
    #  @param kwargs keyword arguments provided to the initialiser.
    def __init__(self, *args:Any, **kwargs:Mapping[str, Any]) -> None:

        self._handle_choices(kwargs)
        self._handle_defaults(kwargs)
        self._handle_action(kwargs)

        super().__init__(*args, **kwargs)

        self.init_kwargs = kwargs.copy()


    ## __init__ 'choices' kwargs actions.
    #  Used during __init__ to capture the 'choices' map, and then reassign it
    #  the mappings keys such that we can use the native actions behavior for
    #  enforcing 'choices' rather than re-inventing the wheel.
    #  @param kwargs keyword arguments provided to the __init__.
    def _handle_choices(self, kwargs:Mapping[str, Any]) -> None:
        
        self.choices_dict = kwargs.pop('choices', {})

        if not isinstance(self.choices_dict, Mapping):
            error_fmt = "'choices' passed to '{}' must be a 'Mapping' type such as 'dict'."
            error_msg = error_fmt.format(self.__class__.__name__)
            raise TypeError(error_msg)

        kwargs['choices'] = list( self.choices_dict.keys() )


    ## __init__ 'default' and 'default_key' kwargs actions.
    #  Used during __init__ to implement the 'default_key' behaviour which 
    #  assigns the 'default' action based on a key in the lookup.
    #  @param kwargs keyword arguments provided to the __init__.
    def _handle_defaults(self, kwargs:Mapping[str, Any]) -> None:

        default_value = kwargs.get('default', None)
        default_key = kwargs.pop('default_key', None)

        if default_value and default_key:
            error_msg = "`default` and `default_key` are mutually exclusive, pick one."
            raise ValueError(error_msg)
        
        if default_key:
            kwargs['default'] = self.get_choice(default_key)


    ## __init__ 'action' kwargs actions.
    #  If this action was create by a call to 'add_argument' on an instance of 
    #  the 'ArgumentParser' then any user assigned 'action' argument will have 
    #  been  forwarded with the 'next_action' argument instead. Its 
    #  recaptured here so we can pass on control after translating the users 
    #  value in '__call__'.
    #  @param kwargs keyword arguments provided to the __init__.
    def _handle_action(self, kwargs:Mapping[str, Any]) -> None:

        self.next_action = kwargs.pop('next_action', None)


    ## Gets the value associate with the choice accompanying this action.
    #  @param choice the choice to get from the choices map.
    #  @returns the value associated with the given choice.
    def get_choice(self, choice:str) -> Any:
        return self.choices_dict[choice]
    

    ## Used to pass on the translated value to the original/native action.
    #  @param parser The ArgumentParser object which contains this action.
    #  @param namespace The Namespace object that will be returned by parse_args().
    #  @param values The associated command-line arguments, after map conversion.
    #  @param option_string The option string that was used to invoke this action.
    def defer_to_next_action(self, parser, namespace, values, option_string) -> None:
        action_class = parser._registry_get('action', self.next_action, self.next_action)
        action_instance = action_class(**self.init_kwargs)
        action_instance(parser, namespace, values, option_string)


    ## Used to convert the CLI argument into its associated map value.
    #  @param parser The ArgumentParser object which contains this action.
    #  @param namespace The Namespace object that will be returned by parse_args().
    #  @param values The associated command-line arguments, with any type conversions applied.
    #  @param option_string The option string that was used to invoke this action.
    def __call__(self, parser, namespace, values, option_string=None):
                
        if isinstance(values, list):
            mapped_value = [ self.get_choice(v) for v in values ]
        else:
            mapped_value = self.get_choice(values)

        self.defer_to_next_action(parser, namespace, mapped_value, option_string)