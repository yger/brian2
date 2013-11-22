import cython
import numpy

from brian2.core.variables import (DynamicArrayVariable, ArrayVariable,
                                   AttributeVariable)
from brian2.core.preferences import brian_prefs, BrianPreference
from brian2.core.functions import DEFAULT_FUNCTIONS, FunctionImplementation, Function

from ...codeobject import CodeObject
from ...templates import Templater
from ...languages.cython_lang import CythonLanguage
from ...targets import codegen_targets
from .modified_inline import modified_cython_inline

__all__ = ['CythonCodeObject']


class CythonCodeObject(CodeObject):
    '''
    '''
    templater = Templater('brian2.codegen.runtime.cython_rt',
                          env_globals={})
    language = CythonLanguage()
    class_name = 'cython'

    def __init__(self, owner, code, namespace, variables, name='cython_code_object*'):
        super(CythonCodeObject, self).__init__(owner, code, namespace, variables, name=name)

    def variables_to_namespace(self):

        # Variables can refer to values that are either constant (e.g. dt)
        # or change every timestep (e.g. t). We add the values of the
        # constant variables here and add the names of non-constant variables
        # to a list

        # A list containing tuples of name and a function giving the value
        self.nonconstant_values = []

        for name, var in self.variables.iteritems():

            try:
                value = var.get_value()
            except TypeError:  # A dummy Variable without value or a Subexpression
                continue

            self.namespace[name] = value

            if isinstance(var, ArrayVariable):
                self.namespace[var.arrayname] = value
                self.namespace['_num'+name] = var.get_len()

            if isinstance(var, DynamicArrayVariable):
                self.namespace[var.name+'_object'] = var.get_object()

            # There are two kinds of objects that we have to inject into the
            # namespace with their current value at each time step:
            # * non-constant AttributeValue (this might be removed since it only
            #   applies to "t" currently)
            # * Dynamic arrays that change in size during runs (i.e. not
            #   synapses but e.g. the structures used in monitors)
            if isinstance(var, AttributeVariable) and not var.constant:
                self.nonconstant_values.append((name, var.get_value))
                if not var.scalar:
                    self.nonconstant_values.append(('_num'+name, var.get_len))
            elif (isinstance(var, DynamicArrayVariable) and
                  not var.constant_size):
                self.nonconstant_values.append((var.arrayname,
                                                var.get_value))
                self.nonconstant_values.append(('_num'+name, var.get_len))

    def update_namespace(self):
        # update the values of the non-constant values in the namespace
        for name, func in self.nonconstant_values:
            self.namespace[name] = func()
        # TODO: what to do about this hack for Cython?
        for k, v in self.namespace.items():
            if isinstance(v, Function):
                if hasattr(v.pyfunc, '_arg_units'):
                    self.namespace[k] = getattr(numpy, v.pyfunc.__name__)
                else:   
                    self.namespace[k] = v.pyfunc
            
    def compile(self):
        CodeObject.compile(self)
#        if hasattr(self.code, 'python_pre'):
#            self.compiled_python_pre = compile(self.code.python_pre, '(string)', 'exec')
#        if hasattr(self.code, 'python_post'):
#            self.compiled_python_post = compile(self.code.python_post, '(string)', 'exec')

    def run(self):
#        if hasattr(self, 'compiled_python_pre'):
#            exec self.compiled_python_pre in self.python_code_namespace
        #return modified_cython_inline(self.code, locals=self.namespace)
        return cython.inline(self.code, locals=self.namespace, globals={})
#        if hasattr(self, 'compiled_python_post'):
#            exec self.compiled_python_post in self.python_code_namespace

codegen_targets.add(CythonCodeObject)
