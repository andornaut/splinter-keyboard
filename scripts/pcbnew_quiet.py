#!/usr/bin/env python3
"""Import KiCad's pcbnew with its harmless startup noise silenced.

pcbnew prints a "PROPERTY_ENUM(): No enum choices defined" wxASSERT to stderr at
import, before wx logging can be configured. The shell wrappers drop it from a
subprocess's stderr via lib.sh's mute_pcbnew_noise, but the in-process importers
(route.py, validate-fab.py) cannot -- the noise is emitted inside this very
process. So swap fd 2 to /dev/null across just the import (nothing else useful is
emitted there); a real import failure still surfaces via the traceback the
interpreter prints after fd 2 is restored.

Use it in place of `import pcbnew`:
    from pcbnew_quiet import pcbnew
"""
import os

_saved_stderr_fd = os.dup(2)
_devnull_fd = os.open(os.devnull, os.O_WRONLY)
os.dup2(_devnull_fd, 2)
try:
    import pcbnew
finally:
    os.dup2(_saved_stderr_fd, 2)
    os.close(_devnull_fd)
    os.close(_saved_stderr_fd)
