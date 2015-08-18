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

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        # If 3 repos have Siteupdates in report three built successfully.
        assert len(updates) == 3

    def test_first_repo_updated(self):
        """ Test to ensure the first repo was updated. """

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[0]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status

    def test_second_repo_updated(self):
        """ Test to ensure the second repo was updated. """

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[1]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status

    def test_third_repo_updated(self):
        """ Test to ensure the third repo was updated. """

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[2]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status
