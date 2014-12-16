try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

	config = {
	'description': 'Drupal updates scripts',
	'author': 'Jim Taylor',
	'url': 'URL to get it at.',
	'download_url': 'https://github.com/jalama/siteUpdates',
	'author_email': 'jim@rootyhollow.com',
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': [drupdates],
	# http://www.scotttorborg.com/python-packaging/minimal.html
	'scripts': [],
	# 'requires'=['gitdb (>=0.6.0)'],
	'name': 'Drupdates'
}

setup(**config)
