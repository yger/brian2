import os

from brian2.core.preferences import brian_prefs


def run():
    '''
    Run brian's test suite. Needs an installation of the nose testing tool.
    '''
    try:
        import nose
    except ImportError:
        raise ImportError('Running the test suite requires the "nose" package.')
    
    dirname = os.path.join(os.path.dirname(__file__), '..')
    return nose.run(argv=['', dirname, '--with-doctest'])


def repeat_with_preferences(opt_list):
    '''
    This decorator is used for testing with different sets of preferences.
    Decorate a test function (note that the test function should not have any
    return value; when using this decorator, nothing is returned) with it and
    give a list of dictionaries as parameters, where each dictionary consists
    of keyword/value combinations for the `brian_prefs` dictionary.
    The preferences are reset to their previous values after the test run.

    Example usage:

        @repeat_with_preferences([{'codegen.target': 'numpy'},
                                  {'codegen.target': 'weave'}])
        def test_something():
            ...
    '''
    def decorator(func):
        def wrapper(*args, **kwds):
            for opts in opt_list:
                # save old preferences
                brian_prefs.backup()
                for key, value in opts.iteritems():
                    brian_prefs[key] = value
                print 'Repeating test %s with options: %s' % (func.__name__, opts)
                func(*args, **kwds)
                # reset preferences
                brian_prefs.restore()

        #make sure that the wrapper has the same name as the original function
        #otherwise nose will ignore the functions as they are not called
        #"test..." anymore!
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__

        return wrapper

    return decorator

if __name__=='__main__':
    run()
