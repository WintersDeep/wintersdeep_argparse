from wintersdeep.argparse import ArgumentParser

integers_to_choose = {
    "one": 1,
    "ten": 10,
    "hundred": 100,
    "thousand": 1000
}

argument_parser = ArgumentParser()
argument_parser.add_argument("-i", "--integer", choices=integers_to_choose, default_key="ten")

arguments = argument_parser.parse_args()
print(f"You chose: {arguments.integer}")