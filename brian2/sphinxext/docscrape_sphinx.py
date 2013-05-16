import re, inspect, textwrap, pydoc
import sphinx
from sphinx.pycode import ModuleAnalyzer

from .docscrape import NumpyDocString, FunctionDoc, ClassDoc

class SphinxDocString(NumpyDocString):
    def __init__(self, docstring, config={}):
        NumpyDocString.__init__(self, docstring, config=config)

    # string conversion routines
    @staticmethod
    def _str_header(name, symbol='`'):
        return ['.. rubric:: ' + name, '']

    @staticmethod
    def _str_field_list(name):
        return [':' + name + ':']

    @staticmethod
    def _str_indent(doc, indent=4):
        out = []
        for line in doc:
            out += [' '*indent + line]
        return out

    def _str_summary(self):
        return self['Summary'] + ['']

    def _str_extended_summary(self):
        return self['Extended summary'] + ['']

    def _str_param_list(self, name):
        out = []
        if self[name]:
            out += self._str_field_list(name)
            out += ['']
            for param, param_type, desc in self[name]:
                out += self._str_indent(['**%s** : %s' % (param.strip(),
                                                          param_type)])
                out += ['']
                out += self._str_indent(desc, 8)
                out += ['']

        return out

    @property
    def _obj(self):
        if hasattr(self, '_cls'):
            return self._cls
        elif hasattr(self, '_f'):
            return self._f
        return None

    def _str_member_list(self):
        """
        Generate a member listing, autosummary:: table .

        """
        out = []

        
        
        for name in ['Instance attributes', 'Class attributes', 'Methods']:
            if not self[name]:
                continue
            
            out += ['.. rubric:: %s' % name, '']
            prefix = getattr(self, '_name', '')

            if prefix:
                prefix = '%s.' % prefix

            autosum = []
            for param, _, _ in self[name]:
                param = param.strip()

                if len(prefix):
                    autosum += ["   ~%s%s" % (prefix, param)]
                else:
                    autosum += ["   %s" % param]

            if autosum:
                out += ['.. autosummary::', '']
                out += autosum
            
            out += ['']
        return out

    def _str_member_docs(self, name):
        """
        Generate the full member autodocs

        """
        out = []

        if self[name]:
            prefix = getattr(self, '_name', '')

            if prefix:
                prefix += '.'

            for param, _, _ in self[name]:
                if name == 'Methods':
                    out += ['.. automethod:: %s%s' % (prefix, param)]
                elif name == 'Instance attributes':
                    out += ['.. autoinstanceattribute:: %s%s' % (prefix, param)]
                elif name == 'Class attributes':
                    out += ['.. autoattribute:: %s%s' % (prefix, param)]
            
            
            out += ['']
        return out

    def _str_section(self, name):
        out = []
        if self[name]:
            out += self._str_header(name)
            out += ['']
            content = textwrap.dedent("\n".join(self[name])).split("\n")
            out += content
            out += ['']
        return out

    def _str_see_also(self, func_role):
        out = []
        if self['See also']:
            see_also = super(SphinxDocString, self)._str_see_also(func_role)
            out = ['.. seealso::', '']
            out += self._str_indent(see_also[2:])
        return out

    def _str_raises(self, name, func_role):
        if not self[name]:
            return []
        out = []
        out += self._str_header(name)
        for func, _, desc in self[name]:
            out += [":exc:`%s`" % func]
            if desc:
                out += self._str_indent([' '.join(desc)])
        out += ['']
        return out        

    def _str_warnings(self):
        out = []
        if self['Warnings']:
            out = ['.. warning::', '']
            out += self._str_indent(self['Warnings'])
        return out

    def _str_index(self):
        idx = self['index']
        out = []
        if len(idx) == 0:
            return out

        out += ['.. index:: %s' % idx.get('default','')]
        for section, references in idx.iteritems():
            if section == 'default':
                continue
            elif section == 'refguide':
                out += ['   single: %s' % (', '.join(references))]
            else:
                out += ['   %s: %s' % (section, ','.join(references))]
        return out

    def _str_references(self):
        out = []
        if self['References']:
            out += self._str_header('References')
            if isinstance(self['References'], str):
                self['References'] = [self['References']]
            out.extend(self['References'])
            out += ['']
            # Latex collects all references to a separate bibliography,
            # so we need to insert links to it
            if sphinx.__version__ >= "0.6":
                out += ['.. only:: latex','']
            else:
                out += ['.. latexonly::','']
            items = []
            for line in self['References']:
                m = re.match(r'.. \[([a-z0-9._-]+)\]', line, re.I)
                if m:
                    items.append(m.group(1))
            out += ['   ' + ", ".join(["[%s]_" % item for item in items]), '']
        return out

    def _str_examples(self):
        return self._str_section('Examples')

    def __str__(self, indent=0, func_role="brianobj"):
        out = []
        out += self._str_index() + ['']
        out += self._str_summary()
        out += self._str_extended_summary()
        for param_list in ('Parameters', 'Returns', 'Other parameters'):
            out += self._str_param_list(param_list)
        for param_list in ('Raises', 'Warns'):
            out += self._str_raises(param_list, func_role)
        out += self._str_warnings()
        out += self._str_see_also(func_role)
        out += self._str_section('Notes')
        out += self._str_references()
        out += self._str_examples()
        out += self._str_member_list()
        if self['Instance attributes'] + self['Class attributes'] + self['Methods']:
            out += ['.. rubric:: Details', '']
            for param_list in ('Instance attributes', 'Class attributes', 'Methods'):
                out += self._str_member_docs(param_list)
        out = self._str_indent(out, indent)
        return '\n'.join(out)

class SphinxFunctionDoc(SphinxDocString, FunctionDoc):
    def __init__(self, obj, doc=None, config={}):
        FunctionDoc.__init__(self, obj, doc=doc, config=config)

class SphinxClassDoc(SphinxDocString, ClassDoc):
    def __init__(self, obj, doc=None, func_doc=None, name=None, config={}):
        self.name = name
        ClassDoc.__init__(self, obj, doc=doc, func_doc=None, config=config)

class SphinxObjDoc(SphinxDocString):
    def __init__(self, obj, doc=None, config={}):
        self._f = obj
        SphinxDocString.__init__(self, doc, config=config)

def get_doc_object(obj, what=None, doc=None, name=None, config={}):
    if what is None:
        if inspect.isclass(obj):
            what = 'class'
        elif inspect.ismodule(obj):
            what = 'module'
        elif callable(obj):
            what = 'function'
        else:
            what = 'object'
    if what == 'class':
        return SphinxClassDoc(obj, func_doc=SphinxFunctionDoc, doc=doc,
                              name=name, config=config)
    elif what in ('function', 'method'):
        return SphinxFunctionDoc(obj, doc=doc, config=config)
    else:
        if doc is None:
            doc = pydoc.getdoc(obj)
        return SphinxObjDoc(obj, doc, config=config)
