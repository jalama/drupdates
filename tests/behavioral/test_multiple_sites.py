""" Test running Drupdates on multiple sites. """
from __future__ import print_function
import os
from tests.behavioral.behavioral_utils import BehavioralUtils
from tests.behavioral.behavioral_utils import BehavioralException
from tests import Setup

class TestMultipleSites(object):

    @classmethod
    def setup_class(cls):
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_first_repo(self):
        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        status = "status : The following updates were applied"
        assert results[4].strip() == status
