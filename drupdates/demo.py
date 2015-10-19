""" Build demostration set-ups. """
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class Demo(object):
    """ Class to help build demos, you run drupdats on the CLI

    The idea is mock a test script's setup and use them to allow you to run the
    drupdates command. Run from inside a python shell in the drupdates folder.

    Sample commands:
    $ git clone git@github.com:jalama/drupdates.git
    $ cd drupdates
    $ pip uninstall drupdates -y; pip install .
    $ python
    >>> from drupdates.demo import Demo
    >>> Demo().setup('test_simple')
    >>> exit()
    $ drupdates
    """

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def setup(self, file_name):
        """ Setup the demo files. """
        utils = BehavioralUtils()
        utils.build(file_name)
