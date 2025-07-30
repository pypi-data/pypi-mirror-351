from argparse import ArgumentParser
from typing import cast


class ArgsDefault:
    verbosity: int = 0


def setup_argument_parser() -> ArgsDefault:
    parser = ArgumentParser()
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="increase output verbosity"
    )
    return cast(ArgsDefault, parser.parse_args())


args = ArgsDefault()
