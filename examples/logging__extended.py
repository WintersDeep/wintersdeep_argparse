from wintersdeep.argparse import ArgumentParser

argument_parser = ArgumentParser()
argument_parser.add_log_level_arguments()
arguments = argument_parser.parse_args()
if log_levels := arguments.log_level:
    log_levels.apply()