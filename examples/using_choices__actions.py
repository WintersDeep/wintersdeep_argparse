from argparse import Action, ArgumentParser
from wintersdeep.argparse import ArgumentParser

class MultipleByThree(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values * 3)


integers_to_choose = {
    "one": 1,
    "ten": 10,
    "hundred": 100,
    "thousand": 1000
}

argument_parser = ArgumentParser()
argument_parser.add_argument("-i", "--integer", choices=integers_to_choose, action=MultipleByThree, default_key="ten")

# NOTE: if you leave the value as default you will still get 10 as actions do not apply to default values
#  this is consistent with the native behaviour - if you want an option that is not in the choices dict
#  remember you can use default just like normal (i.e. default=30).

arguments = argument_parser.parse_args()
print(f"You chose: {arguments.integer}")