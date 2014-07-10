
#from .api import command


def iscallable(obj):
    if hasattr(obj, '__call__'):
        return True
    return False


def ensure_list(obj):
    if not isinstance(obj, (list, tuple)):
        return [obj]
    return obj


#def list_commands():
#    pass

#command('show', list_commands)
