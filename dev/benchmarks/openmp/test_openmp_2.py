import sys, os, numpy, time, pylab

filename = 'STDP_standalone.py'
datapath = 'STDP'
threads  = [1, 2, 4, 6]
results  = {}
results['duration'] = []

for t in threads:
    start = time.time()
    os.system('python %s 1 %d' %(filename, t))
    results['duration'] += [time.time()-start]
    results[t]           = {}

for t in threads:
    results[t]  = {}
    path        = datapath + '_%d/' %t
    ids         = numpy.fromfile(path+'results/spikemonitor_codeobject_i', dtype=numpy.int32)
    times       = numpy.fromfile(path+'results/spikemonitor_codeobject_t', dtype=numpy.float64)
    w           = numpy.fromfile(path+'results/_dynamic_array_synapses_w', dtype=numpy.float64)
    times_2     = numpy.fromfile(path+'results/statemonitor_codeobject_t', dtype=numpy.float64)
    w_over_time = numpy.fromfile(path+'results/statemonitor_codeobject_w', dtype=numpy.float64)
    results[t]['spikes']  = (times, ids)
    results[t]['w']       = w
    results[t]['trace_w'] = (times_2, w_over_time)

pylab.figure()
pylab.subplot(221)
pylab.title('Raster plots')
pylab.xlabel('Time [s]')
pylab.ylabel('# cell')
for t in threads:
    pylab.plot(results[t]['spikes'][0], results[t]['spikes'][1], '.')
pylab.legend(map(str, threads))
pylab.xlim(0.5, 0.55)

pylab.subplot(222)
pylab.title('Weight Evolution')
pylab.xlabel('Time [s]')
pylab.ylabel('Weight [ns]')
for t in threads:
    pylab.plot(results[t]['trace_w'][0], results[t]['trace_w'][1])
pylab.legend(map(str, threads))

pylab.subplot(223)
pylab.title('Final Distribution')
pylab.xlabel('Weight [ns]')
pylab.ylabel('Number of synapses')
for t in threads:
    x, y = numpy.histogram(results[t]['w'], 100)
    pylab.plot(y[1:], x)
pylab.legend(map(str, threads))

pylab.subplot(224)
pylab.title('Speed')
pylab.plot(threads, results['duration'])
pylab.xlabel('# threads')
pylab.ylabel('Time [s]')

pylab.savefig('STDP_openmp.png')

pylab.show()