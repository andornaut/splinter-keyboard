"""Import KiCad's pcbnew with its harmless noise silenced.

Two separate sources, so two separate guards:

  1. At import, pcbnew prints a "PROPERTY_ENUM(): No enum choices defined"
     wxASSERT to stderr, before wx logging can be configured. The shell wrappers
     drop it from a subprocess's stderr via common.sh's mute_pcbnew_noise, but the
     in-process importers cannot -- the noise is emitted inside this very
     process. So swap fd 2 to /dev/null across just the import (nothing else
     useful is emitted there); a real import failure still surfaces via the
     traceback the interpreter prints after fd 2 is restored.

  2. Later, on the first LoadBoard, wx logs a run of "Adding duplicate image
     handler" debug lines. Those come too late for the import guard, so raise
     the wx log level past Debug and Info instead. Warnings and errors still
     print, so a real wx complaint is not hidden.

Use it in place of `import pcbnew`:
    from lib.pcbnew_quiet import pcbnew
"""

import os

_saved_stderr_fd = os.dup(2)
_devnull_fd = os.open(os.devnull, os.O_WRONLY)
os.dup2(_devnull_fd, 2)
try:
    import pcbnew  # noqa: F401  # re-exported; this module exists to import it quietly
finally:
    os.dup2(_saved_stderr_fd, 2)
    os.close(_devnull_fd)
    os.close(_saved_stderr_fd)

try:
    import wx

    wx.Log.SetLogLevel(wx.LOG_Warning)
except (ImportError, AttributeError):
    # wx ships with pcbnew, so this should not happen; the debug lines are
    # cosmetic, so a missing or changed wx is not worth failing the run over.
    pass
