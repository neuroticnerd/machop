
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
    error = False
    for f in fileset:
        result = call(['flake8', f], shell=True)
        if result != 0:
            error = True
    if not error:
        print "machop: python linting passed"
