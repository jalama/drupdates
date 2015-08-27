""" Test running Drupdates on one repo. """
from __future__ import print_function
import os
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestDrushMakeWebroot(object):
    """ Test running Drupdates on one repo. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_repo_built(self):
        """ Test to ensure one repo built successfully. """

        count = BehavioralUtils.count_repos_updated('builds')
        # If 1 repo Siteupdates in report repo built successfully.
        assert count == 1


    def test_repo_updated(self):
        """ Test to ensure the repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated(self.test_directory, 'dmake_webroot', 'builds')
        assert report_status == status
