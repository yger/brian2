import os
import shutil
import sphinx
import sys

os.chdir('../../../docs_sphinx')
if os.path.exists('../docs'):
    shutil.rmtree('../docs')
 
print '** Building docs **'
exit_code = sphinx.main(['sphinx-build', '-b', 'html', '.', '../docs'])

if exit_code == 0:
    print '** Testing doctests in the docs **'

    sys.exit(sphinx.main(['sphinx-build', '-b', 'doctest', '.', '../docs']))
else:
    print 'Building docs failed'
    sys.exit(exit_code)