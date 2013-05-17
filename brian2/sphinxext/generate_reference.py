# -*- coding: utf-8 -*-
"""
    Automatically generate Brian's reference documentation.
    
    Based on sphinx-apidoc, published under a BSD license: http://sphinx-doc.org/
"""
import inspect
import sys
import os
import shutil
from os import path

INITPY = '__init__.py'

OPTIONS = ['show-inheritance']

SUFFIX = '.rst'
# Helper functions 

def makename(package, module):
    """Join package and module with a dot."""
    # Both package and module can be None/empty.
    if package:
        name = package
        if module:
            name += '.' + module
    else:
        name = module
    return name


def format_heading(level, text):
    """Create a heading of <level> [1, 2 or 3 supported]."""
    underlining = ['=', '-', '~', ][level-1] * len(text)
    return '%s\n%s\n\n' % (text, underlining)


def shall_skip(module):
    """Check if we want to skip this module."""
    # skip it if there is nothing (or just \n or \r\n) in the file
    return path.getsize(module) <= 2


def normalize_excludes(rootpath, excludes):
    """
    Normalize the excluded directory list:
    * must be either an absolute path or start with rootpath,
    * otherwise it is joined with rootpath
    * with trailing slash
    """
    f_excludes = []
    for exclude in excludes:
        if not path.isabs(exclude) and not exclude.startswith(rootpath):
            exclude = path.join(rootpath, exclude)
        f_excludes.append(path.normpath(exclude) + path.sep)
    return f_excludes


def is_excluded(root, excludes):
    """
    Check if the directory is in the exclude list.

    Note: by having trailing slashes, we avoid common prefix issues, like
          e.g. an exlude "foo" also accidentally excluding "foobar".
    """
    sep = path.sep
    if not root.endswith(sep):
        root += sep
    for exclude in excludes:
        if root.startswith(exclude):
            return True
    return False

# The main class generating the reference docs 

class ReferenceGenerator(object):
    
    def __init__(self, rootdir, excludes, targetdir, basename):
        self.rootdir = rootdir
        self.excludes = excludes
        self.targetdir = targetdir
        self.basename = basename

    def write_file(self, name, text):
        """Write the output file for module/package <name>."""
        fname = path.join(self.targetdir, '%s%s' % (name, SUFFIX))
        
        if os.path.exists(fname):
            # Check whether we would overwrite a file with identical content
            # --> this would make sphinx assume that the file changed
            with open(fname, 'r') as f:
                previous = f.read()
                if previous == text:
                    return  # no need to overwrite the file
        
        print 'Creating file %s' % fname
            
        with open(fname, 'w') as f:
            f.write(text)

    def format_directive(self, module, package=None, toctree=True):
        """Create the automodule directive and add the options."""
        directive = '.. automodule:: %s\n' % makename(package, module)
        for option in OPTIONS:
            directive += '    :%s:\n' % option
        directive += '\n'
        # document all the classes in the modules
        full_name = self.basename + '.' + module
        __import__(full_name)
        mod = sys.modules[full_name]
        dir_members = dir(mod)
        classes = []
        functions = []
        variables = []
        for member in dir_members:
            _temp = __import__(full_name, {}, {}, [member], 0)
            member_obj = getattr(_temp, member)
            member_module = getattr(member_obj, '__module__', None)
            # only document members that where defined in this module
            if member_module == full_name and not member.startswith('_'):
                if inspect.isclass(member_obj):
                    classes.append((member, member_obj))
                elif inspect.isfunction(member_obj):
                    functions.append((member, member_obj))
                else:
                    variables.append((member, member_obj))
        
        if classes:
            directive += '**Classes**\n\n'
            for member, member_obj in classes:
                directive += '.. autosummary:: %s\n' % (member)
                if toctree:
                    directive += '    :toctree:\n\n'
                else:
                    directive += '\n'
                self.create_member_file(full_name, member, member_obj, toctree)
        if functions:
            directive += '**Functions**\n\n'
            for member, member_obj in functions:
                directive += '.. autosummary:: %s\n' % (member)
                if toctree:
                    directive += '    :toctree:\n\n'
                else:
                    directive += '\n'                
                self.create_member_file(full_name, member, member_obj, toctree)
        if variables:
            directive += '**Objects**\n\n'
            for member, member_obj in variables:
                directive += '.. autosummary:: %s\n' % (member)
                if toctree:
                    directive += '    :toctree:\n\n'
                else:
                    directive += '\n'                
                self.create_member_file(full_name, member, member_obj, toctree)
                    
        return directive


    def create_member_file(self, module_name, member, member_obj, toctree):
        """Build the text of the file and write the file."""
        
        if not toctree:
            # Suppress warnings about documents that are not included in any
            # doctree if we specifically asked for it in the first place
            text = ':orphan:\n\n'
        else:
            text = ''
    
        text += '.. currentmodule:: ' + module_name + '\n\n'
        
        if inspect.isclass(member_obj):
            text += format_heading(1, '%s class' % member)
            text += '.. autoclass:: %s\n\n' % member
        elif inspect.isfunction(member_obj):
            text += format_heading(1, '%s function' % member)
            text += '.. autofunction:: %s\n\n' % member
        else:
            text += format_heading(1, '%s object' % member)
            text += '.. autodata:: %s\n' % member
    
        self.write_file(makename(module_name, member), text)


    def create_package_file(self, root, master_package, subroot, py_files, subs):
        """Build the text of the file and write the file."""
        package = path.split(root)[-1]
        text = format_heading(1, '%s package' % package)
        # add each module in the package
        for py_file in py_files:
            if shall_skip(path.join(root, py_file)):
                continue
            is_package = py_file == INITPY
            py_file = path.splitext(py_file)[0]
            py_path = makename(subroot, py_file)
            # we don't want an additional header for the package,
            if not is_package:
                heading = ':mod:`%s` module' % py_file
                text += format_heading(2, heading)
            
            # We don't want functions directly declared in a package to appear in
            # its toctree -- otherwiese restore_initial_state would appear on the
            # reference overview as it is defined in brian2.__init__
            # We don't have any code (except for imports) in packages anywhere
            # except in the top-level brian2 package, so this is a special case
            toctree = not is_package
            text += self.format_directive(is_package and subroot or py_path,
                                     master_package, toctree=toctree)
            text += '\n'
    
        # build a list of directories that are packages (contain an INITPY file)
        subs = [sub for sub in subs if path.isfile(path.join(root, sub, INITPY))]
        # if there are some package directories, add a TOC for theses subpackages
        if subs:
            text += format_heading(2, 'Subpackages')
            text += '.. toctree::\n'
            text += '    :maxdepth: 2\n\n'
            for sub in subs:
                if not is_excluded(os.path.join(self.rootdir, sub), self.excludes):
                    text += '    %s.%s\n' % (makename(master_package, subroot), sub)
            text += '\n'
    
        self.write_file(makename(master_package, subroot), text)


    def recurse_tree(self):
        """
        Look for every file in the directory tree and create the corresponding
        ReST files.
        """

        # check if the base directory is a package and get its name
        if INITPY in os.listdir(self.rootdir):
            root_package = self.rootdir.split(path.sep)[-1]
        else:
            # otherwise, the base is a directory with packages
            root_package = None
    
        toplevels = []
        for root, subs, files in os.walk(self.rootdir):
            if is_excluded(root, self.excludes):
                del subs[:]
                continue
            # document only Python module files
            py_files = sorted([f for f in files if path.splitext(f)[1] == '.py'])
            is_pkg = INITPY in py_files
            if is_pkg:
                py_files.remove(INITPY)
                py_files.insert(0, INITPY)
            elif root != self.rootdir:
                # only accept non-package at toplevel
                del subs[:]
                continue
            # remove hidden ('.') and private ('_') directories
            subs[:] = sorted(sub for sub in subs if sub[0] not in ['.', '_'])
    
            if is_pkg:
                # we are in a package with something to document
                if subs or len(py_files) > 1 or not \
                    shall_skip(path.join(root, INITPY)):
                    subpackage = root[len(self.rootdir):].lstrip(path.sep).\
                        replace(path.sep, '.')
                    self.create_package_file(root, root_package, subpackage,
                                             py_files, subs)
                    toplevels.append(makename(root_package, subpackage))
            else:
                raise AssertionError('Expected it to be a package')
    
        return toplevels


def main():
    target_dir = './reference'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    abs_root = os.path.abspath('../brian2')    
    excludes = normalize_excludes(abs_root, ['tests', 'sphinxext'])
    
    generator = ReferenceGenerator(abs_root, excludes, target_dir,
                                   basename='brian2')
    
    generator.recurse_tree()
