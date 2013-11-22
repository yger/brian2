import itertools

import numpy
import numpy as np

from brian2.utils.stringtools import (deindent, stripped_deindented_lines,
                                      word_substitute)
from brian2.utils.logger import get_logger
from brian2.core.functions import (Function, FunctionImplementation,
                                   DEFAULT_FUNCTIONS)
from brian2.core.preferences import brian_prefs, BrianPreference
from brian2.core.variables import ArrayVariable, DynamicArrayVariable

from .base import Language

logger = get_logger(__name__)

__all__ = ['CythonLanguage',
           ]


class CythonLanguage(Language):
    '''
    '''

    language_id = 'cython'

    def __init__(self):
        pass

    def translate_expression(self, expr, namespace, codeobj_class):
#        for varname, var in namespace.iteritems():
#            if isinstance(var, Function):
#                impl_name = var.implementations[codeobj_class].name
#                if impl_name is not None:
#                    expr = word_substitute(expr, {varname: impl_name})
        return expr.strip()

    def translate_statement(self, statement, namespace, codeobj_class):
        var, op, expr = statement.var, statement.op, statement.expr
        if op==':=':
            op = '='
        expr = self.translate_expression(expr, namespace, codeobj_class)
        return var + ' ' + op + ' ' + expr

    def translate_one_statement_sequence(self, statements, variables, namespace,
                                         variable_indices, iterate_all,
                                         codeobj_class):

        read, write, indices = self.array_read_write(statements, variables,
                                                     variable_indices)
        lines = []
        # index and read arrays (index arrays first)
        for varname in itertools.chain(indices, read):
            index_var = variable_indices[varname]
            var = variables[varname]
#            if varname not in write:
#                line = 'const '
#            else:
#                line = ''
#            line = line + self.c_data_type(var.dtype) + ' ' + varname + ' = '
            line = '{varname} = {arrayname}[{index}]'.format(varname=varname, arrayname=var.arrayname,
                                                             index=index_var)
#            line = line + '_ptr' + var.arrayname + '[' + index_var + '];'
            lines.append(line)
#        # simply declare variables that will be written but not read
#        for varname in write:
#            if varname not in read:
#                var = variables[varname]
#                line = self.c_data_type(var.dtype) + ' ' + varname + ';'
#                lines.append(line)
        # the actual code
        lines.extend([self.translate_statement(stmt, namespace, codeobj_class)
                      for stmt in statements])
        # write arrays
        for varname in write:
            index_var = variable_indices[varname]
            var = variables[varname]
            line = '{arrayname}[{index}] = {varname}'.format(varname=varname, arrayname=var.arrayname,
                                                             index=index_var)
            #line = '_ptr' + var.arrayname + '[' + index_var + '] = ' + varname + ';'
            lines.append(line)
        code = '\n'.join(lines)
                
        return stripped_deindented_lines(code)

    def determine_keywords(self, variables, namespace, codeobj_class):
        return {}
#        # set up the restricted pointers, these are used so that the compiler
#        # knows there is no aliasing in the pointers, for optimisation
#        lines = []
#        # It is possible that several different variable names refer to the
#        # same array. E.g. in gapjunction code, v_pre and v_post refer to the
#        # same array if a group is connected to itself
#        arraynames = set()
#        for varname, var in variables.iteritems():
#            if isinstance(var, ArrayVariable):
#                arrayname = var.arrayname
#                if not arrayname in arraynames:
#                    if getattr(var, 'dimensions', 1) > 1:
#                        continue  # multidimensional (dynamic) arrays have to be treated differently
#                    line = self.c_data_type(var.dtype) + ' * ' + self.restrict + '_ptr' + arrayname + ' = ' + arrayname + ';'
#                    lines.append(line)
#                    arraynames.add(arrayname)
#        pointers = '\n'.join(lines)
#
#        # set up the functions
#        user_functions = []
#        support_code = ''
#        hash_defines = ''
#        for varname, variable in namespace.items():
#            if isinstance(variable, Function):
#                user_functions.append((varname, variable))
#                speccode = variable.implementations[codeobj_class].code
#                if speccode is not None:
#                    support_code += '\n' + deindent(speccode.get('support_code', ''))
#                    hash_defines += deindent(speccode.get('hashdefine_code', ''))
#                # add the Python function with a leading '_python', if it
#                # exists. This allows the function to make use of the Python
#                # function via weave if necessary (e.g. in the case of randn)
#                if not variable.pyfunc is None:
#                    pyfunc_name = '_python_' + varname
#                    if pyfunc_name in namespace:
#                        logger.warn(('Namespace already contains function %s, '
#                                     'not replacing it') % pyfunc_name)
#                    else:
#                        namespace[pyfunc_name] = variable.pyfunc
#
#        # delete the user-defined functions from the namespace and add the
#        # function namespaces (if any)
#        for funcname, func in user_functions:
#            del namespace[funcname]
#            func_namespace = func.implementations[codeobj_class].namespace
#            if func_namespace is not None:
#                namespace.update(func_namespace)
#
#        return {'pointers_lines': stripped_deindented_lines(pointers),
#                'support_code_lines': stripped_deindented_lines(support_code),
#                'hashdefine_lines': stripped_deindented_lines(hash_defines),
#                'denormals_code_lines': stripped_deindented_lines(self.denormals_to_zero_code()),
#                }

    def translate_statement_sequence(self, statements, variables, namespace,
                                     variable_indices, iterate_all,
                                     codeobj_class):
        if isinstance(statements, dict):
            blocks = {}
            for name, block in statements.iteritems():
                blocks[name] = self.translate_one_statement_sequence(block,
                                                                     variables,
                                                                     namespace,
                                                                     variable_indices,
                                                                     iterate_all,
                                                                     codeobj_class)
        else:
            blocks = self.translate_one_statement_sequence(statements, variables,
                                                           namespace, variable_indices,
                                                           iterate_all, codeobj_class)

        kwds = self.determine_keywords(variables, namespace, codeobj_class)

        return blocks, kwds


################################################################################
# Implement functions
################################################################################
# Functions that exist under the same name in numpy
for func_name, func in [('sin', np.sin), ('cos', np.cos), ('tan', np.tan),
                        ('sinh', np.sinh), ('cosh', np.cosh), ('tanh', np.tanh),
                        ('exp', np.exp), ('log', np.log), ('log10', np.log10),
                        ('sqrt', np.sqrt), ('ceil', np.ceil),
                        ('floor', np.floor), ('arcsin', np.arcsin),
                        ('arccos', np.arccos), ('arctan', np.arctan),
                        ('abs', np.abs), ('mod', np.mod)]:
    DEFAULT_FUNCTIONS[func_name].implementations[CythonLanguage] = FunctionImplementation(code=func)

# Functions that are implemented in a somewhat special way
def randn_func(vectorisation_idx):
    try:
        N = int(vectorisation_idx)
    except (TypeError, ValueError):
        N = len(vectorisation_idx)

    return np.random.randn(N)

def rand_func(vectorisation_idx):
    try:
        N = int(vectorisation_idx)
    except (TypeError, ValueError):
        N = len(vectorisation_idx)

    return np.random.rand(N)
DEFAULT_FUNCTIONS['randn'].implementations[CythonLanguage] = FunctionImplementation(code=randn_func)
DEFAULT_FUNCTIONS['rand'].implementations[CythonLanguage] = FunctionImplementation(code=rand_func)
clip_func = lambda array, a_min, a_max: np.clip(array, a_min, a_max)
DEFAULT_FUNCTIONS['clip'].implementations[CythonLanguage] = FunctionImplementation(code=clip_func)
int_func = lambda value: np.int_(value)
DEFAULT_FUNCTIONS['int_'].implementations[CythonLanguage] = FunctionImplementation(code=int_func)
