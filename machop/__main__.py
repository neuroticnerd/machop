# -*- coding: utf-8 -*-
import sys
import os
import imp
import colorama
import machop  # @@@ does this need to be done differently if not installed?

from .strings import ascii_machop, ascii_fainted, ascii_choose_you
from .strings import txt_startup_msg, txt_config_error


def main():
    """
    creates the CLI for machop
    """
    CONFIG_MODULE = 'karatechop'
    CONFIG_FILENAME = CONFIG_MODULE + '.py'
    args = sys.argv[1:]
    exit_code = 0
    karatechop = None
    CWD = os.getcwd()
    colorama.init()
    try:
        meta = ('.py', 'rb', imp.PY_SOURCE)
        filepath = os.path.join(CWD, CONFIG_FILENAME)
        with open(filepath, 'rb') as kfile:
            karatechop = imp.load_module(CONFIG_MODULE, kfile, filepath, meta)
            if not karatechop:
                raise ValueError("error accessing karatechop module")
    except (ImportError, IOError):
        print txt_config_error
        exit_code = 1
        raise SystemExit(exit_code > 0)
    # running specific commands
    if len(args) > 0:
        for command in args:
            # @@@ TODO use argparse to config params to commands
            machop.run(command, cmdpath=CWD)
    # running default command
    else:
        print ascii_choose_you
        print ascii_machop
        print txt_startup_msg
        # @@@ TODO use argparse to config params to commands
        machop.run('focus-energy', cmdpath=CWD)
    machop.api._wait()
    print ascii_fainted
    raise SystemExit(exit_code > 0)
