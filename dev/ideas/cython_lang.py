from pylab import *
from brian2 import *
from brian2.parsing.rendering import NodeRenderer, CPPNodeRenderer, NumpyNodeRenderer
from brian2.codegen.languages.cython_lang import CythonLanguage
from brian2.codegen.statements import Statement
from brian2.codegen.translation import make_statements
from brian2.core.variables import Variable, ArrayVariable

code = '''
x = a*b+c
'''

#print NodeRenderer().render_code(code)
#print CPPNodeRenderer().render_code(code)
#print NumpyNodeRenderer().render_code(code)

lang = CythonLanguage()

#print lang.translate_expression('a*b+c', {}, None)
#print lang.translate_statement(Statement('x', '=', 'a*b+c', float), {}, None)

stmts = make_statements(code, {}, float)
#for stmt in stmts:
#    print stmt

variables = {'a':ArrayVariable('a', Unit(1), zeros(10)),
             'b':ArrayVariable('b', Unit(1), zeros(10)),
             'x':ArrayVariable('x', Unit(1), zeros(10)),
             }
namespace = {}
variable_indices = {'a': '_idx', 'b': '_idx', 'x': '_idx'}
    
print '\n'.join(lang.translate_one_statement_sequence(stmts, variables, namespace, variable_indices, True, None))
