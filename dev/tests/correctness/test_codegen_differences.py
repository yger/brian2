'''
Performs the same simulation (without any random elements) with different
settings (numpy vs. C code, different C code optimization settings) and assures
that the results are always identical.
'''
import numpy as np
import matplotlib.pyplot as plt

from brian2 import *
from brian2.tests import repeat_with_preferences


def setup_test_cobahh():
    ''' load the matrices once to save some time '''
    
    # Load the connections
    print 'Loading connection matrices'
    Ce_matrix = np.loadtxt('Ce_matrix.txt.gz')
    Ci_matrix = np.loadtxt('Ci_matrix.txt.gz')
    
    print 'Loading reference spikes'
    reference_spikes = np.loadtxt('COBAHH_spikes.txt.gz')

    return Ce_matrix, Ci_matrix, reference_spikes


@repeat_with_preferences([{'codegen.target': 'numpy'},
                          {'codegen.target': 'weave',
                           'codegen.runtime.weave.extra_compile_args': ['-O0']},
                          {'codegen.target': 'weave',
                           'codegen.runtime.weave.extra_compile_args': ['-O3', '-ffast-math', '-march=native']}])
def test_cobahh():
    '''
    Test the COBAHH example with different optimizations (weave, etc.).
    '''
    defaultclock.t = 0*ms
    
    # Parameters
    area = 20000 * umetre ** 2
    Cm = (1 * ufarad * cm ** -2) * area
    gl = (5e-5 * siemens * cm ** -2) * area
    El = -60 * mV
    EK = -90 * mV
    ENa = 50 * mV
    g_na = (100 * msiemens * cm ** -2) * area
    g_kd = (30 * msiemens * cm ** -2) * area
    VT = -63 * mV
    # Time constants
    taue = 5 * ms
    taui = 10 * ms
    # Reversal potentials
    Ee = 0 * mV
    Ei = -80 * mV
    
    # The model
    eqs = Equations('''
    dv/dt = (gl*(El-v)+ge*(Ee-v)+gi*(Ei-v)-\
        g_na*(m*m*m)*h*(v-ENa)-\
        g_kd*(n*n*n*n)*(v-EK))/Cm : volt 
    dm/dt = alpham*(1-m)-betam*m : 1
    dn/dt = alphan*(1-n)-betan*n : 1
    dh/dt = alphah*(1-h)-betah*h : 1
    dge/dt = -ge*(1./taue) : siemens
    dgi/dt = -gi*(1./taui) : siemens
    alpham = 0.32*(mV**-1)*(13*mV-v+VT)/ \
        (exp((13*mV-v+VT)/(4*mV))-1.)/ms : Hz
    betam = 0.28*(mV**-1)*(v-VT-40*mV)/ \
        (exp((v-VT-40*mV)/(5*mV))-1)/ms : Hz
    alphah = 0.128*exp((17*mV-v+VT)/(18*mV))/ms : Hz
    betah = 4./(1+exp((40*mV-v+VT)/(5*mV)))/ms : Hz
    alphan = 0.032*(mV**-1)*(15*mV-v+VT)/ \
        (exp((15*mV-v+VT)/(5*mV))-1.)/ms : Hz
    betan = .5*exp((10*mV-v+VT)/(40*mV))/ms : Hz
    ''')

    # TODO: The refractoriness semantics are slightly different than in Brian1
    #       maybe only for EmpiricalThreshold, though
    P = NeuronGroup(4000, model=eqs, threshold='v>-20*mV', refractory=2.96*ms,
                    method='exponential_euler')
    Pe = P[:3200]
    Pi = P[3200:]

    Ce_matrix, Ci_matrix, reference_spikes = setup_test_cobahh()
    print 'Setting up connections'
    we = 6 * nS # excitatory synaptic weight (voltage)
    wi = 67 * nS # inhibitory synaptic weight
    Ce = Synapses(Pe, P, pre='ge += we')
    pre, post = Ce_matrix.nonzero()
    Ce.connect(pre, post)
    Ci = Synapses(Pi, P, pre='gi += wi')
    pre, post = Ci_matrix.nonzero()
    Ci.connect(pre, post)
    
    # Initialization (non-random)
    P.v = El + ((np.arange(len(P), dtype=np.float) / len(P) - 0.5) * 20 - 5) * mV
    P.ge = ((np.arange(len(P), dtype=np.float) / len(P) - 0.5) * 6 + 4) * 10. * nS
    P.gi = ((np.arange(len(P), dtype=np.float) / len(P) - 0.5) * 48 + 20) * 10. * nS
    
    mon = SpikeMonitor(P)
    record = [1000, 2000, 3000]
    v_mon = StateMonitor(P, 'v', record=record)

    print 'Starting simulation'
    net = Network(P, Ce, Ci, mon, v_mon)
    net.run(1 * second, report='text')
    
    # compare results to the saved spikes
    spikes = np.array(mon.it).T
    sys.stdout.flush()
    if spikes.shape != reference_spikes.shape:
        sys.stderr.write('Spike array shapes do not match: %s vs. %s\n' %
                         (str(spikes.shape), str(reference_spikes.shape)))
    elif not (spikes == reference_spikes).all():
        sys.stderr.write('Array content is not identical\n')
    else:
        print 'All spikes are equal.'

    plt.subplot(2, 1, 1)
    plt.plot(v_mon.t / ms, v_mon.v.T / mV)
    plt.ylabel('v (mV)')
    plt.xlim(0, 1000)
    plt.subplot(2, 1, 2)
    plt.plot(mon.t / ms, mon.i, '.')
    plt.xlim(0, 1000)
    plt.xlabel('time (ms)')
    plt.show()


if __name__ == '__main__':
    test_cobahh()