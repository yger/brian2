from pylab import *
from scipy import weave

def compute_on_range(funcname, in_arr, fastmath=False):
    out_arr = zeros(len(in_arr))
    if fastmath:
        compile_args = ['-O3', '-ffast-math', '-march=native']
    else:
        compile_args = ['-O3', '-march=native']
    code = '''
    // COMPILE_ARGS
    for(int i=0; i<N; i++)
    {
        out_arr[i] = funcname(in_arr[i]);
    }
    '''.replace('funcname', funcname).replace('COMPILE_ARGS', str(compile_args))
    ns = {'in_arr': in_arr, 'out_arr': out_arr, 'N': len(in_arr)}
    weave.inline(code, ns.keys(), ns, extra_compile_args=compile_args)
    return out_arr

N = 10000
funcs = {
    'sin': linspace(-100, 100, N),
    'cos': linspace(-10000, 10000, N),
    'exp': linspace(-100, 100, N),
    }

for i, (funcname, in_arr) in enumerate(funcs.items()):
    subplot(2, len(funcs), i+1)
    out_arr_slow = compute_on_range(funcname, in_arr)
    out_arr_fast = compute_on_range(funcname, in_arr, fastmath=True)
    err = out_arr_slow-out_arr_fast
    plot(in_arr, out_arr_slow-out_arr_fast)
    title(funcname+' abs error')

    subplot(2, len(funcs), len(funcs)+i+1)
    plot(in_arr, err/out_arr_slow)
    title(funcname+' rel error')
    
tight_layout()
show()
