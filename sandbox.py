from argparse import Action
from wintersdeep.argparse import ArgumentParser

class AddPrefix(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, lambda x: f"Your number is {values(x)}")

argument_parser = ArgumentParser()
argument_parser.add_argument("N", type=int)
action = argument_parser.add_argument("-f", "--formatter", 
  action=AddPrefix,
  choices={
    "bin": lambda n: f"{n:b}",
    "oct": lambda n: f"{n:o}",
    "hex": lambda n: f"{n:x}"
}, default_key='hex')

arguments = argument_parser.parse_args()

print("action", action.__class__.__name__)
print("next_action", action.next_action)
print( arguments.formatter(arguments.N) )

