'''
Base class for generating code in different programming languages, gives the
methods which should be overridden to implement a new language.
'''
from brian2.core.variables import ArrayVariable
from brian2.utils.stringtools import get_identifiers
from brian2.codegen.translation import make_statements

__all__ = ['CodeGenerator']

class CodeGenerator(object):
    '''
    Base class for all languages.
    
    See definition of methods below.
    
    TODO: more details here
    '''

    # Subclasses should override this
    generator_id = ''

    def __init__(self, variables, variable_indices, iterate_all, codeobj_class,
                 override_conditional_write=None):
        # We have to do the import here to avoid circular import dependencies.
        from brian2.devices.device import get_device
        self.device = get_device()
        self.variables = variables
        self.variable_indices = variable_indices
        self.iterate_all = iterate_all
        self.codeobj_class = codeobj_class
        if override_conditional_write is None:
            self.override_conditional_write = set()
        else:
            self.override_conditional_write = set(override_conditional_write)

    @staticmethod
    def get_array_name(var, access_data=True):
        '''
        Get a globally unique name for a `ArrayVariable`.

        Parameters
        ----------
        var : `ArrayVariable`
            The variable for which a name should be found.
        access_data : bool, optional
            For `DynamicArrayVariable` objects, specifying `True` here means the
            name for the underlying data is returned. If specifying `False`,
            the name of object itself is returned (e.g. to allow resizing).
        Returns
        -------
        name : str
            A uniqe name for `var`.
        '''
        # We have to do the import here to avoid circular import dependencies.
        from brian2.devices.device import get_device
        device = get_device()
        return device.get_array_name(var, access_data=access_data)

    def translate_expression(self, expr):
        '''
        Translate the given expression string into a string in the target
        language, returns a string.
        '''
        raise NotImplementedError

    def translate_statement(self, statement):
        '''
        Translate a single line `Statement` into the target language, returns
        a string.
        '''
        raise NotImplementedError

    def translate_statement_sequence(self, statements):
        '''
        Translate a sequence of `Statement` into the target language, taking
        care to declare variables, etc. if necessary.
   
        Returns a tuple ``(code_lines, kwds)`` where ``code_lines`` is a list
        of the lines of code in the inner loop, and ``kwds`` is a
        dictionary of values that is made available to the template.
        '''
        raise NotImplementedError

    def array_read_write(self, statements):
        '''
        Helper function, gives the set of ArrayVariables that are read from and
        written to in the series of statements. Returns the pair read, write
        of sets of variable names.
        '''
        variables = self.variables
        variable_indices = self.variable_indices
        read = set()
        write = set()
        for stmt in statements:
            ids = set(get_identifiers(stmt.expr))
            # if the operation is inplace this counts as a read.
            if stmt.inplace:
                ids.add(stmt.var)
            read = read.union(ids)
            write.add(stmt.var)
        read = set(varname for varname, var in variables.items()
                   if isinstance(var, ArrayVariable) and varname in read)
        write = set(varname for varname, var in variables.items()
                    if isinstance(var, ArrayVariable) and varname in write)
        # Gather the indices stored as arrays (ignore _idx which is special)
        indices = set()
        indices |= set(variable_indices[varname] for varname in read
                       if not variable_indices[varname] in ('_idx', '0')
                           and isinstance(variables[variable_indices[varname]],
                                          ArrayVariable))
        indices |= set(variable_indices[varname] for varname in write
                       if not variable_indices[varname] in ('_idx', '0')
                           and isinstance(variables[variable_indices[varname]],
                                          ArrayVariable))
        # don't list arrays that are read explicitly and used as indices twice
        read -= indices
        return read, write, indices

    def get_conditional_write_vars(self):
        '''
        Helper function, returns a dict of mappings ``(varname, condition_var_name)`` indicating that
        when ``varname`` is written to, it should only be when ``condition_var_name`` is ``True``.
        '''
        conditional_write_vars = {}
        for varname, var in self.variables.items():
            if getattr(var, 'conditional_write', None) is not None:
                cvar = var.conditional_write
                cname = cvar.name
                if cname not in self.override_conditional_write:
                    conditional_write_vars[varname] = cname
        return conditional_write_vars

    def arrays_helper(self, statements):
        '''
        Combines the two helper functions `array_read_write` and `get_conditional_write_vars`, and updates the
        ``read`` set.
        '''
        read, write, indices = self.array_read_write(statements)
        conditional_write_vars = self.get_conditional_write_vars()
        read = read.union(set(conditional_write_vars.values()) |
                          set(conditional_write_vars.keys()))
        return read, write, indices, conditional_write_vars

    def translate(self, code, dtype):
        '''
        Translates an abstract code block into the target language.
        '''
        statements = {}
        for ac_name, ac_code in code.iteritems():
            statements[ac_name] = make_statements(ac_code, self.variables, dtype)
        return self.translate_statement_sequence(statements)
