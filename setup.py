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
	version = '0.5',
	package_dir = {'drupdates' : 'drupdates'},
  include_package_data = True,
	install_requires = ['nose', 'gitpython', 'requests', 'pyyaml'],
	entry_points = {
		'console_scripts': ['drupdates = drupdates:main'],
	},
	packages = ['drupdates'],
)

