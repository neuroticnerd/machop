# -*- coding: utf-8 -*-
# @@@ import argparse in future for better cli arg handling
import sys
import os
import machop

def main():
    """
    creates the CLI for machop
    """
    # config = os.path.join(os.getcwd(), 'karatechop.py')
    args = sys.argv[1:]
    exit_code = 0
    try:
        setup = __import__('karatechop')
    except ImportError as e:
        print "\nconfig module could not be loaded!\n"
        print "hint: is your config in the current working directory?"
        print "hint: is your config named 'karatechop.py'?"
        exit_code = 1
        raise SystemExit(exit_code > 0)
    cwd = os.getcwd()
    if len(args) > 0:
        for command in args:
            # @@@ TODO use argparse to config params to commands
            machop.run(command, cmdpath=cwd)
    else:
        # @@@ TODO use argparse to config params to commands
        machop.run('focus-energy', cmdpath=cwd)
    raise SystemExit(exit_code > 0)

if __name__ == "__main__":
    main()
