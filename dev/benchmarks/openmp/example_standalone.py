#!/usr/bin/env python
# coding: latin-1
"""
CUBA example with delays.
"""

import sys, time
from brian2 import *

standalone = int(sys.argv[-2])
n_threads  = int(sys.argv[-1])

if standalone == 1:
    set_device('cpp_standalone')

start      = time.time()
n_cells    = 10

numpy.random.seed(42)
connectivity = numpy.abs(numpy.random.randn(n_cells, n_cells))

taum       = 20 * ms
taus       = 5 * ms
Vt         = -50 * mV
Vr         = -60 * mV
El         = -49 * mV

fac        = (60 * 0.27 / 10)  # excitatory synaptic weight (voltage)

gmax       = 20*fac
dApre      = .01
taupre     = 20 * ms
taupost    = taupre
dApost     = -dApre * taupre / taupost * 1.05
dApost    *=  gmax
dApre     *=  gmax


eqs  = Equations('''
dv/dt  = (g-(v-El))/taum : volt
dg/dt = -g/taus : volt
''')

P    = NeuronGroup(n_cells, model=eqs, threshold='v>Vt', reset='v=Vr', refractory=5 * ms)
P.v  = Vr + numpy.random.rand(len(P)) * (Vt - Vr)
P.g  = 0 * mV



S    = Synapses(P, P, 
                    model = '''dApre/dt=-Apre/taupre    : 1 (event-driven)    
                               dApost/dt=-Apost/taupost : 1 (event-driven)
                               w                        : 1''', 
                    pre = '''g += w*mV
                             Apre += dApre
                             w = clip(w + Apost, 0, gmax)''',
                    post = '''Apost += dApost
                             w = clip(w + Apre, 0, gmax)''',
                    connect=True)
S.w  = fac*connectivity.flatten()


spike_mon = SpikeMonitor(P)
state_mon = StateMonitor(S, 'w', record=range(n_cells*n_cells), when=Clock(dt=0.1*second))
v_mon     = StateMonitor(P, 'v', record=True)

run(0.5 * second)
if standalone == 1:
    device.build(project_dir='data_example_%d' %n_threads, compile_project=True, run_project=True, debug=False, n_threads=n_threads)