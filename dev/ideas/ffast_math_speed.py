from pylab import *
from scipy import weave
import timeit

N = 100000
x = zeros(N)
y = zeros(N)
code = '''
/// %s
for(int i=0; i<N; i++)
  y[i] = exp(x[i]);
'''
ns = {'x': x, 'N': N, 'y':y}

def with_numpy():
    exp(x)
    
def with_weave(*args):
    weave.inline(code % str(args), ns.keys(), ns, extra_compile_args=list(args))
    
def with_weave_slow():
    with_weave('-O3', '-march=native')
    
def with_weave_fast():
    with_weave('-O3', '-ffast-math', '-march=native')
    
with_numpy()
with_weave_slow()
with_weave_fast()

if __name__=='__main__':
    for name in ['numpy', 'weave_slow', 'weave_fast']:
        t = timeit.timeit('with_%s()' % name, 'from __main__ import with_%s' % name, number=10000000/N)
        print '%s: %.2d ms' % (name, t*1000)
