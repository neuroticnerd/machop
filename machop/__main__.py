import os

from .cli import MachopCLI


def run_machop_cli():
    machop = MachopCLI()
    machop.runcli(os.getcwd())

if __name__ == "__main__":
    run_machop_cli()
