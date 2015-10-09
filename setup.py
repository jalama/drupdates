""" Drupdates setup script. """
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Drupdates',
    description='Drupal updates scripts',
    author='Jim Taylor',
    url='https://github.com/jalama/drupdates',
    download_url='https://github.com/jalama/drupdates',
    author_email='jalama@gmail.com',
    version='1.5.0',
    package_dir={'drupdates' : 'drupdates', 'drupdates.tests' : 'drupdates/tests'},
    include_package_data=True,
    install_requires=['nose', 'gitpython', 'requests', 'pyyaml'],
    entry_points={
        'console_scripts': ['drupdates = drupdates.cli:main'],
    },
    packages=['drupdates', 'drupdates.tests'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Bug Tracking',
    ],
)
