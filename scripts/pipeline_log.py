#!/usr/bin/env python3
"""The quiet half of the pipeline's log voice (the convention itself is at the top
of scripts/lib.sh).

A line that reports something happening, or something asking to be read, is a plain
print and always shows. A line that only confirms nothing needed doing goes through
`note` and shows only under PIPELINE_VERBOSE: a clean run of ten steps is otherwise
mostly the word "ok", and each step's closing OK: summary already carries the count
those lines would have added up to.

The switch is an environment variable rather than a flag because a run is a dozen
processes deep (wrappers calling helpers calling helpers), and every one of them
has to agree on how loud it is. `npm run pipeline -- -v` sets it for all of them;
see pipeline.sh. lib.sh has the bash `note` for the wrappers.

Not an entry point: import it, do not run it.
"""
import os

VERBOSE = bool(os.environ.get("PIPELINE_VERBOSE"))


def note(line):
    """Print a line that only confirms nothing needed doing, under PIPELINE_VERBOSE.

    Takes the whole formatted line, so a call site reads the same as the print it
    replaced and the convention stays legible at the point of use."""
    if VERBOSE:
        print(line)
