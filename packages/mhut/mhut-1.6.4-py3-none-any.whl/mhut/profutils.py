import cProfile
from line_profiler import LineProfiler

# decorator version of profiler
def std_profile(funcref):
    def inner(*args, **kwargs):
        print ('INFO. profiling', funcref.__name__)
        prof = cProfile.Profile()
        result = prof.runcall(funcref, *args, **kwargs)
        prof.print_stats()
        return result
    return inner

# func wrapper form of profiler
def std_profile_wrap(funcref, *args, **kwargs):
    prof = cProfile.Profile()
    result = prof.runcall(funcref, *args, **kwargs)
    prof.print_stats()
    return result


#Borrowed & adapted from Brian Helmig: https://zapier.com/engineering/profiling-python-boss/
def line_profile(follow=()):
    def inner(func):
        def profiled_func(*args, **kwargs):
            try:
                profiler = LineProfiler()
                profiler.add_function(func)
                for f in follow:
                    profiler.add_function(f)
                profiler.enable_by_count()
                return func(*args, **kwargs)
            finally:
                profiler.print_stats()
        return profiled_func
    return inner


