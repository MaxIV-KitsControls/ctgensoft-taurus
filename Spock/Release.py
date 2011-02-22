# -*- coding: utf-8 -*-
"""Release data for the Spock project.
"""

# Name of the package for release purposes.  This is the name which labels
# the tarballs and RPMs made by distutils, so it's best to lowercase it.
name = 'spock'

# For versions with substrings (like 0.6.16.svn), use an extra . to separate
# the new substring.  We have to avoid using either dashes or underscores,
# because bdist_rpm does not accept dashes (an RPM) convention, and
# bdist_deb does not accept underscores (a Debian convention).

revision = '1'

#version = '0.8.1.svn.r' + revision.rstrip('M')
version = '0.1'

description = "An enhanced interactive Macro Server shell."

long_description = \
"""
Spock provides an interactive environment for interacting with the Tango
MacroServer Device. It is completely based on IPython which itself provides a 
replacement for the interactive Python interpreter with extra functionality.
 """

license = 'GNU'

authors = {'Tiago'     : ('Tiago Coutinho','tcoutinho@cells.es'),
           'Alejandro' : ('Alejandro Homs','homs@esrf.eu'),
           'Vicente'   : ('Vicente Rey-Bakaikoa','vicente.rey@esrf.eu') 
           }

url = ''

download_url = ''

platforms = ['Linux','Mac OSX','Windows XP/2000/NT','Windows 95/98/ME']

keywords = ['Interactive','MacroServer','Tango','Shell']
