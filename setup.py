try:
	from setuptools import setup, find_packages
except ImportError:
	from distutils.core import setup, find_packages
import sys

# Ensure Python verison is >= 2.6
# http://stackoverflow.com/questions/13924931/setup-py-restrict-the-allowable-version-of-the-python-interpreter
if not sys.version_info[0] < 2 and sys.version_info[1] < 7:
    print "Python version needs to exceed 2.6"
    sys.exit(1) # return non-zero value for failure

setup (
	name = 'Drupdates',
	description = 'Drupal updates scripts',
	author = 'Jim Taylor',
	url = 'https://github.com/jalama/drupdates',
	download_url = 'https://github.com/jalama/drupdates',
	author_email = 'jim@rootyhollow.com',
	version = '1.0.4',
	package_dir = {'drupdates' : 'drupdates'},
  include_package_data = True,
	install_requires = ['nose', 'gitpython', 'requests', 'pyyaml'],
	entry_points = {
		'console_scripts': ['drupdates = drupdates.updates:main'],
	},
	packages = ['drupdates'],
	classifiers=[
	  'Development Status :: 4 - Beta',
	  'Environment :: Console',
	  'Intended Audience :: Developers',
	  'Intended Audience :: System Administrators',
	  'License :: OSI Approved :: MIT License',
	  'Natural Language :: English',
	  'Operating System :: MacOS :: MacOS X',
	  'Operating System :: POSIX',
	  'Programming Language :: Python',
	  'Programming Language :: Python :: 2',
	  'Programming Language :: Python :: 2.6',
	  'Programming Language :: Python :: 2.7',
	  'Topic :: System :: Systems Administration',
	  'Topic :: Software Development :: Build Tools',
	  'Topic :: Software Development :: Bug Tracking',
	  ],
)

