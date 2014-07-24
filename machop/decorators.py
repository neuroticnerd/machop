
from functools import wraps


class kwargs(object):
    """ adds additional keyword arguments to a command """
    def __init__(self, **kwargs):
        self.extrakwargs = {}
        for k, v in kwargs.iteritems():
            self.extrakwargs[k] = v
        print self.extrakwargs

    def __call__(self, func):
        @wraps(func)
        def add_params(**kwargs):
            for key, val in self.extrakwargs.iteritems():
                kwargs[key] = val
            return func(**kwargs)
        return add_params
