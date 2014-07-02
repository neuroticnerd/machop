
from subprocess import call

def flake(pythonfiles):
    """
    pythonfiles can be a directory, file, or list/tuple of files
    TODO: collect output from flake calls
    """
    fileset = []
    if isinstance(pythonfiles, (list, tuple)):
        fileset = pythonfiles
    else:
        fileset = [pythonfiles]
    for f in fileset:
        call(['flake8', f], shell=True)
