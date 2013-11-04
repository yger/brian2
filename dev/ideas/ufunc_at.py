import ast
from brian2 import *
from brian2.codegen.languages.numpy_lang import rewrite_for_ufunc_at#, InplaceRenderer
from brian2.parsing.rendering import NodeRenderer, NumpyNodeRenderer


indices = {
    'Apre': '_idx_syn',
    'Apost': '_idx_syn',
    'lastupdate': '_idx_syn',
    'ge': '_idx_post',
    'w': '_idx_syn',
    }

repeated_indices = set(['_idx_post'])

statements = [
    Statement('Apre', '=', 'Apre * exp(-(t - lastupdate) / taupre)', float),
    Statement('Apost', '=', 'Apost * exp(-(t - lastupdate) / taupost)', float),
    Statement('ge', '=', 'ge+w', float),
    Statement('Apre', '+=', 'dApre', float),
    Statement('w', '=', 'clip(w + Apost, 0, gmax)', float),
    Statement('lastupdate', '=', 't', float),
    ]

new_statements, success = rewrite_for_ufunc_at(statements, indices, repeated_indices)
print success
for statement in new_statements:
    print statement
