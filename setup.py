#! /usr/bin/env python
'''
Brian2 setup script
'''
import sys
import os

# This will automatically download setuptools if it is not already installed
from ez_setup import use_setuptools
use_setuptools()

import pkg_resources
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.errors import CompileError

try:
    from Cython.Build import cythonize
    cython_available = True
except ImportError:
    cython_available = False


def has_option(name):
    try:
        sys.argv.remove('--%s' % name)
        return True
    except ValueError:
        pass
    # allow passing all cmd line options also as environment variables
    env_val = os.getenv(name.upper().replace('-', '_'), 'false').lower()
    if env_val == "true":
        return True
    return False


WITH_CYTHON = has_option('with-cython')
FAIL_ON_ERROR = has_option('fail-on-error')

pyx_fname = os.path.join('brian2', 'synapses', 'cythonspikequeue.pyx')
cpp_fname = os.path.join('brian2', 'synapses', 'cythonspikequeue.cpp')

if WITH_CYTHON or not os.path.exists(cpp_fname):
    fname = pyx_fname
    if not cython_available:
        if FAIL_ON_ERROR:
            raise RuntimeError('Compilation with Cython requested/necesary but '
                               'Cython is not available.')
        else:
            sys.stderr.write('Compilation with Cython requested/necesary but '
                             'Cython is not available.\n')
            fname = None
    if not os.path.exists(pyx_fname):
        if FAIL_ON_ERROR:
            raise RuntimeError(('Compilation with Cython requested/necessary but '
                                'Cython source file %s does not exist') % pyx_fname)
        else:
            sys.stderr.write(('Compilation with Cython requested/necessary but '
                                'Cython source file %s does not exist\n') % pyx_fname)
            fname = None
else:
    fname = cpp_fname

if fname is not None:
    extensions = [Extension("brian2.synapses.cythonspikequeue",
                            [fname],
                            include_dirs=[])]  # numpy include dir will be added later
    if fname == pyx_fname:
        extensions = cythonize(extensions)
else:
    extensions = []


class optional_build_ext(build_ext):
    '''
    This class allows the building of C extensions to fail and still continue
    with the building process. This ensures that installation never fails, even
    on systems without a C compiler, for example.
    If brian is installed in an environment where building C extensions
    *should* work, use the "--fail-on-error" option or set the environment
    variable FAIL_ON_ERROR to true.
    '''
    def build_extension(self, ext):
        import numpy
        numpy_incl = numpy.get_include()
        if hasattr(ext, 'include_dirs') and not numpy_incl in ext.include_dirs:
                ext.include_dirs.append(numpy_incl)
        try:
            build_ext.build_extension(self, ext)
        except CompileError as ex:
            if FAIL_ON_ERROR:
                raise ex
            else:
                error_msg = ('Building %s failed (see error message(s) '
                             'above) -- pure Python version will be used '
                             'instead.') % ext.name
                sys.stderr.write('*' * len(error_msg) + '\n' +
                                 error_msg + '\n' +
                                 '*' * len(error_msg) + '\n')

long_description = '''
Brian2 is a simulator for spiking neural networks available on almost all platforms.
The motivation for this project is that a simulator should not only save the time of
processors, but also the time of scientists.

It is the successor of Brian1 and shares its approach of being highly flexible
and easily extensible. It is based on a code generation framework that allows
to execute simulations using other programming languages and/or on different
devices.

We currently consider this software to be in the alpha status, please report
issues to the github issue tracker (https://github.com/brian-team/brian2/issues) or to the
brian-development mailing list (http://groups.google.com/group/brian-development/)

Documentation for Brian2 can be found at http://brian2.readthedocs.org
'''

setup(name='Brian2',
      version='2.0a7',
      packages=find_packages(),
      package_data={# include template files
                    'brian2.codegen.runtime.numpy_rt': ['templates/*.py_'],
                    'brian2.codegen.runtime.weave_rt': ['templates/*.cpp',
                                                        'templates/*.h'],
                    'brian2.devices.cpp_standalone': ['templates/*.cpp',
                                                      'templates/*.h',
                                                      'templates/makefile',
                                                      'brianlib/*.cpp',
                                                      'brianlib/*.h'],
                    # include C++ version of spike queue
                    'brian2.synapses': ['*.cpp'],
                    # include default_preferences file
                    'brian2': ['default_preferences']
                    },
      install_requires=['numpy>=1.4.1',
                        'scipy>=0.7.0',
                        'sympy>=0.7.2',
                        'pyparsing',
                        'jinja2>=2.7',
                       ],
      setup_requires=['numpy>=1.4.1'],
      cmdclass={'build_ext': optional_build_ext},
      provides=['brian2'],
      extras_require={'test': ['nosetests>=1.0'],
                      'docs': ['sphinx>=1.0.1', 'sphinxcontrib-issuetracker']},
      use_2to3=True,
      ext_modules=extensions,
      url='http://www.briansimulator.org/',
      description='A clock-driven simulator for spiking neural networks',
      long_description=long_description,
      author='Marcel Stimberg, Dan Goodman, Romain Brette',
      author_email='Romain.Brette at ens.fr',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Bio-Informatics'
      ]
      )
