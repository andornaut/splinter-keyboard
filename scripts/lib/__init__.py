"""Shared helpers the pipeline's entry points import.

Everything importable lives in this directory and nothing else does, so what a
file is answers to `ls` rather than to a naming convention: shell and Python read
the same way, and a one-word name gives nothing away. `common.sh` is the bash
half, sourced by the wrappers.

Entry points sit one level up and import from here as `lib.<module>`, which
resolves because Python puts a script's own directory on sys.path regardless of
the working directory. Modules in here import each other relatively.
"""
