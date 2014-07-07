# -*- coding: utf-8 -*-
import sys
import os
import imp
import machop


def main():
    """
    creates the CLI for machop
    """
    CONFIG_MODULE = 'karatechop'
    CONFIG_FILENAME = CONFIG_MODULE + '.py'
    invocation_path = sys.argv[0]
    args = sys.argv[1:]
    exit_code = 0
    CWD = os.getcwd()
    karatechop = None
    try:
        meta = ('.py', 'rb', imp.PY_SOURCE)
        filepath = os.path.join(CWD, CONFIG_FILENAME)
        with open(filepath, 'rb') as kfile:
            karatechop = imp.load_module(CONFIG_MODULE, kfile, filepath, meta)
    except (ImportError, IOError):
        print "\nconfig module could not be loaded!\n"
        print "hint: is your config in the current working directory?"
        print "hint: is your config named 'karatechop.py'?"
        exit_code = 1
        raise SystemExit(exit_code > 0)
    if len(args) > 0:
        for command in args:
            # @@@ TODO use argparse to config params to commands
            machop.run(command, cmdpath=CWD)
    else:
        # @@@ TODO use argparse to config params to commands
        machop.run('focus-energy', cmdpath=CWD)
    raise SystemExit(exit_code > 0)
