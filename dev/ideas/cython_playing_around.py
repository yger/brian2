from pylab import *
import cython
import time, timeit
from brian2.codegen.runtime.cython_rt.modified_inline import modified_cython_inline
import numpy
from scipy import weave

tau = 20 * 0.001
N = 1000000
b = 1.2 # constant current mean, the modulation varies
freq = 10.0
t = 0.0
dt = 0.0001

_array_neurongroup_a = a = linspace(.05, 0.75, N)
_array_neurongroup_v = v = rand(N)

ns = {'_array_neurongroup_a': a, '_array_neurongroup_v': v,
      '_N': N,
      'dt': dt, 't': t, 'tau': tau, 'b': b, 'freq': freq,# 'sin': numpy.sin,
      'pi': pi,
      }

code = '''
cdef int _idx
cdef int _vectorisation_idx
cdef int N = <int>_N
cdef double a, v, _v
#cdef double [:] _cy_array_neurongroup_a = _array_neurongroup_a
#cdef double [:] _cy_array_neurongroup_v = _array_neurongroup_v
cdef double* _cy_array_neurongroup_a = &(_array_neurongroup_a[0])
cdef double* _cy_array_neurongroup_v = &(_array_neurongroup_v[0])
for _idx in range(N):
    _vectorisation_idx = _idx
    a = _cy_array_neurongroup_a[_idx]
    v = _cy_array_neurongroup_v[_idx]
    _v = a*sin(2.0*freq*pi*t) + b + v*exp(-dt/tau) + (-a*sin(2.0*freq*pi*t) - b)*exp(-dt/tau)
    #_v = a*b+0.0001*sin(v)
    #_v = a*b+0.0001*v 
    v = _v
    _cy_array_neurongroup_v[_idx] = v
'''
def timefunc_cython_inline():
    cython.inline(code, locals=ns)

f_mod, f_arg_list = modified_cython_inline(code, locals=ns, globals={})
def timefunc_cython_modified_inline():
    f_mod.__invoke(*f_arg_list)
    #modified_cython_inline(code, locals=ns)

def timefunc_python():
    for _idx in xrange(N):
        _vectorisation_idx = _idx
        a = _array_neurongroup_a[_idx]
        v = _array_neurongroup_v[_idx]
        _v = a*sin(2.0*freq*pi*t) + b + v*exp(-dt/tau) + (-a*sin(2.0*freq*pi*t) - b)*exp(-dt/tau)
        v = _v
        _array_neurongroup_v[_idx] = v
        
def timefunc_numpy():
    _v = a*sin(2.0*freq*pi*t) + b + v*exp(-dt/tau) + (-a*sin(2.0*freq*pi*t) - b)*exp(-dt/tau)
    v[:] = _v
    
def timefunc_weave(*args):
    code = '''
    // %s
    int N = _N;
    for(int _idx=0; _idx<N; _idx++)
    {
        double a = _array_neurongroup_a[_idx];
        double v = _array_neurongroup_v[_idx];
        double _v = a*sin(2.0*freq*pi*t) + b + v*exp(-dt/tau) + (-a*sin(2.0*freq*pi*t) - b)*exp(-dt/tau);
        v = _v;
        _array_neurongroup_v[_idx] = v;
    }
    ''' % str(args)
    weave.inline(code, ns.keys(), ns, compiler='gcc', extra_compile_args=list(args))
    
def timefunc_weave_slow():
    timefunc_weave('-O3', '-march=native')

def timefunc_weave_fast():
    timefunc_weave('-O3', '-march=native', '-ffast-math')

def dotimeit(f):
    f()
    print '%s: %.2f' % (f.__name__.replace('timefunc_', ''),
                        timeit.timeit(f.__name__+'()', setup='from __main__ import '+f.__name__, number=100)) 

if __name__=='__main__':
    if 0:
        # check accuracy
        v[:] = 1
        timefunc_weave()
        print v[:5]
        v[:] = 1
        timefunc_cython_inline()
        print v[:5]
        v[:] = 1
        timefunc_numpy()
        print v[:5]
    if 1:
        #dotimeit(timefunc_cython_inline)
        v[:] = 1
        dotimeit(timefunc_cython_modified_inline)
        #dotimeit(timefunc_python)
        v[:] = 1
        dotimeit(timefunc_numpy)
        v[:] = 1
        dotimeit(timefunc_weave_slow)
        v[:] = 1
        dotimeit(timefunc_weave_fast)
        