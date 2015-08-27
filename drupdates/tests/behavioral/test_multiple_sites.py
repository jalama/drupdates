""" Test running Drupdates on multiple sites. """
from __future__ import print_function
import os
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestMultipleSites(object):
    """ Test running Drupdates on multiple sites. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_all_repos_built(self):
        """ Test to ensure all three repos built successfully. """

        count = BehavioralUtils.count_repos_updated('builds')
        # If 3 repos Siteupdates in report repo built successfully.
        assert count == 3

    def test_first_repo_updated(self):
        """ Test to ensure the first repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated(self.test_directory, 'drupal', 'builds')
        assert report_status == status

    def test_second_repo_updated(self):
        """ Test to ensure the second repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated(self.test_directory, 'drupal2', 'builds')
        assert report_status == status

    def test_third_repo_updated(self):
        """ Test to ensure the third repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated(self.test_directory, 'drupal3', 'builds')
        assert report_status == status
