try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': 'Drupal updates scripts',
	'author': 'Jim Taylor',
	'url': 'URL to get it at.',
	'download_url': 'https://github.com/jalama/drupdates',
	'author_email': 'jim@rootyhollow.com',
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': ['drupdates'],
	'package_dir': {'drupdates': 'drupdates'},
	'install_requires': ['gitpython', 'requests', 'pyyaml'],
	'name': 'Drupdates'
}

setup(**config)
