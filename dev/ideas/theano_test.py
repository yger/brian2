from pylab import *
import theano
from theano import tensor as tt
import time

x = tt.dvector('x')
y = tt.dvector('y')
t = tt.dscalar('t')

expr = lambda x, y, t: x+y*2*3*4*tt.sin(t)
#expr = lambda x, y: x+y

f = theano.function([x, y, t], expr(x, y, t))

N = 100000
repeats = 100

a = linspace(0, 1, N)
b = a[::-1].copy()
t = 1.0

start = time.time()
for _ in xrange(repeats):
    f(a, b, t)
end = time.time()

print 'theano: %.2f' % (end-start)

start = time.time()
for _ in xrange(repeats):
    expr(a, b, t)
end = time.time()

print 'numpy: %.2f' % (end-start)