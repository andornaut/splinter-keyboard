#!/usr/bin/env python3
"""The two board stages, and the argument every validator uses to scope itself.

`unrouted/` is where routing is done and `routed/` holds the masters fab exports
from. Every validator runs over both by default and takes an optional positional
argument naming one, so this is the vocabulary plus the wiring that reads it.

It lives here rather than in each validator because the argparse call carries a
non-obvious workaround, and three copies of a workaround is three chances to fix
it in only two of them.

Not an entry point: import it, do not run it.
"""

STAGES = ("unrouted", "routed")


def add_stage_argument(parser, help_text):
    """Add the optional positional stage scope.

    default=None rather than list(STAGES): argparse validates the default against
    `choices` as well as the parsed values, and a list is not one of the choices,
    so a list default makes every no-argument run fail."""
    parser.add_argument(
        "stages", nargs="*", choices=STAGES, default=None, help=help_text
    )


def selected(args):
    """The stages to run over: those named, or all of them."""
    return args.stages or list(STAGES)
