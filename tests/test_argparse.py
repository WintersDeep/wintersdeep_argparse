# python3 imports
from io import IOBase
from typing import Any
from unittest import TestCase
from contextlib import redirect_stderr
from argparse import Action

# project imports
from wintersdeep.argparse import ArgumentParser


## Dummy writer 
# used to redirect stderr text emitted by the underlying
# argument parser
class DevNull(IOBase):
    def write(self, *args, **kwargs) -> Any:
        pass

## Common user action
#  Used to test the the original user action is still executed when using
#  mapping choices.
class MutlipleByThree(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values * 3)


## The unit tests themselves.
class ArgumentParserUnittests(TestCase):

    
    ## Ran once before all test in this case are ran.
    @classmethod
    def setUpClass(cls) -> None:
        cls.numeric_choices = {
            "one": 1,
            "ten": 10,
            "hundred": 100,
            "thousand": 1000
        }
        return super().setUpClass()

    ## Ran before each test to setup the instance.
    def setUp(self) -> None:
        self.argument_parser = ArgumentParser()
        return super().setUp()


    ## Test that none of the really basic behaviours of argparse have been
    #  broken by the shim (better safe than sorry).
    def test_no_choices_still_works(self):
        self.argument_parser.add_argument("-s", type=str)
        self.assertEqual(self.argument_parser.parse_args(["-s", "a"]).s, "a")
        self.assertEqual(self.argument_parser.parse_args(["-s", "x"]).s, "x")


    ## Test that default value still work as expected.
    def test_no_choices_default_still_works(self):
        self.argument_parser.add_argument("-s", type=str, default="unset")
        self.assertEqual(self.argument_parser.parse_args(["-s", "any"]).s, "any")
        self.assertEqual(self.argument_parser.parse_args([]).s, "unset")


    ## Test that list based choices still function properly.
    def test_list_choices_still_works_positive(self):
        self.argument_parser.add_argument("-s", type=str, choices=["a", "b", "c"])
        self.assertEqual(self.argument_parser.parse_args(["-s", "a"]).s, "a")
        self.assertEqual(self.argument_parser.parse_args(["-s", "b"]).s, "b")
        self.assertEqual(self.argument_parser.parse_args(["-s", "c"]).s, "c")
        self.assertIsNone(self.argument_parser.parse_args([]).s)
        

    ## Tests that list based values still actually enforce their choice.
    def test_list_choices_still_works_negative(self):
        self.argument_parser.add_argument("-s", type=str, required=True, choices=["a", "b", "c"])
        with redirect_stderr(DevNull()):
            with self.assertRaises(SystemExit): self.argument_parser.parse_args(["-s", "d"])
            with self.assertRaises(SystemExit): self.argument_parser.parse_args(["-s", "e"])
            with self.assertRaises(SystemExit): self.argument_parser.parse_args(["-s", "f"])
            with self.assertRaises(SystemExit): self.argument_parser.parse_args([])


    ## Tests that list based choices still properly honour their default value.
    def test_list_choices_with_default_still_works(self):
        self.argument_parser.add_argument("-s", type=str, choices=["a", "b", "c"], default="unset")
        self.assertEqual(self.argument_parser.parse_args(["-s", "a"]).s, "a")
        self.assertEqual(self.argument_parser.parse_args([]).s, "unset")


    ## Test that the basic functionality provided by this library works.
    def test_basic_mapping_choices_positive(self):
        self.argument_parser.add_argument("-s", type=str, choices=self.numeric_choices)
        self.assertEqual(self.argument_parser.parse_args(["-s", "one"]).s, 1)
        self.assertEqual(self.argument_parser.parse_args(["-s", "ten"]).s, 10)
        self.assertEqual(self.argument_parser.parse_args(["-s", "hundred"]).s, 100)
        self.assertIsNone(self.argument_parser.parse_args([]).s)


    ## Test that the basic functionality also enforces its constraints.
    def test_basic_mapping_choices_negative(self):
        self.argument_parser.add_argument("-s", type=str, required=True, choices=self.numeric_choices)
        with redirect_stderr(DevNull()):
            with self.assertRaises(SystemExit): self.argument_parser.parse_args(["-s", "ONE"])
            with self.assertRaises(SystemExit): self.argument_parser.parse_args(["-s", "three"])
            with self.assertRaises(SystemExit): self.argument_parser.parse_args([])

    
    ## Tests that defaults applied to mapped choices function.
    def test_map_choices_with_default(self):
        self.argument_parser.add_argument("-s", type=str, choices=self.numeric_choices, default=-999)
        self.assertEqual(self.argument_parser.parse_args(["-s", "one"]).s, 1)
        self.assertEqual(self.argument_parser.parse_args([]).s, -999)

    
    ## Tests the the default_key keyword is working as expected.
    def test_map_choices_with_default_key(self):
        self.argument_parser.add_argument("-s", type=str, choices=self.numeric_choices, default_key="thousand")
        self.assertEqual(self.argument_parser.parse_args(["-s", "one"]).s, 1)
        self.assertEqual(self.argument_parser.parse_args([]).s, 1000)


    ## Tests the the `default_key` keyword causes an error for non-supporting types.
    def test_nonmap_choices_with_default_key(self):
        with redirect_stderr(DevNull()):
            with self.assertRaises(TypeError): self.argument_parser.add_argument("-s", type=str, choices=["a", "b", "c"], default_key=0)
            with self.assertRaises(TypeError): self.argument_parser.add_argument("-s", type=str, choices=["a", "b", "c"], default_key="a")
            with self.assertRaises(TypeError): self.argument_parser.add_argument("-s", type=str, default_key="a")


    ## Test that default_key and default are mutually exclusive - there can be only one default.
    def test_map_choices_with_default_key_and_default_value(self):
        with redirect_stderr(DevNull()):
            with self.assertRaises(ValueError): self.argument_parser.add_argument("-s", type=str, choices=self.numeric_choices, default_key="thousand", default=999)
                

    ## Test that you get an immediate error (without actually having to parse something) if you 
    #  specify a default_key that does not exist in the choices map.
    def test_map_choices_with_bad_default_key(self):
        with redirect_stderr(DevNull()):
            with self.assertRaises(KeyError): self.argument_parser.add_argument("-s", type=str, choices=self.numeric_choices, default_key="doesnt-exist")


    ## Tests that the shim hasn't broken the basic 'action' behaviour.
    def test_user_actions_still_applied_no_choices(self):
        self.argument_parser.add_argument("-s", action=MutlipleByThree, default=10, type=int)
        self.assertEqual(self.argument_parser.parse_args(["-s", "1"]).s, 3)
        self.assertEqual(self.argument_parser.parse_args(["-s", "2"]).s, 6)
        self.assertEqual(self.argument_parser.parse_args(["-s", "3"]).s, 9)
        self.assertEqual(self.argument_parser.parse_args([]).s, 10)


    ## Test that user `action` arguments are still effective when using mapped choices
    def test_user_actions_still_applied_with_choices(self):
        self.argument_parser.add_argument("-s", action=MutlipleByThree, choices=[1,2,3], default=10, type=int)
        self.assertEqual(self.argument_parser.parse_args(["-s", "1"]).s, 3)
        self.assertEqual(self.argument_parser.parse_args(["-s", "2"]).s, 6)
        self.assertEqual(self.argument_parser.parse_args(["-s", "3"]).s, 9)
        self.assertEqual(self.argument_parser.parse_args([]).s, 10)


    ## Test that the default does not run through any user 'action' on a mapped choice.
    def test_user_actions_applied_on_map_with_default(self):
        arg = self.argument_parser.add_argument("-s", action=MutlipleByThree, choices=self.numeric_choices, default=999)
        self.assertEqual(self.argument_parser.parse_args(["-s", "one"]).s, 3)
        self.assertEqual(self.argument_parser.parse_args(["-s", "ten"]).s, 30)
        self.assertEqual(self.argument_parser.parse_args(["-s", "hundred"]).s, 300)
        self.assertEqual(self.argument_parser.parse_args([]).s, 999)
        self.assertEqual(arg.next_action, MutlipleByThree)


    ## Test that a default_key default does not run through any user 'action' on a mapped choice.
    def test_user_actions_applied_on_map_with_default_key(self):
        arg = self.argument_parser.add_argument("-s", action=MutlipleByThree, choices=self.numeric_choices, default_key="ten")
        self.assertEqual(self.argument_parser.parse_args(["-s", "one"]).s, 3)
        self.assertEqual(self.argument_parser.parse_args(["-s", "ten"]).s, 30)
        self.assertEqual(self.argument_parser.parse_args(["-s", "hundred"]).s, 300)
        self.assertEqual(self.argument_parser.parse_args([]).s, 10)
        self.assertEqual(arg.next_action, MutlipleByThree)


