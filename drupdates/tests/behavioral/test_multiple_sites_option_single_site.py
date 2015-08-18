""" Test multiple sites, passing singleSite option on CLI. """

"""
    note: Only the one site, labeled 'drupal' should be updated.
"""
import os
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestMultipleSiteOptionSingleSite(object):
    """ Test multiple sites, passing singleSite option on CLI. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_one_repo_built(self):
        """ Test to ensure one of three repos built successfully. """

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        # If 1 repo has Siteupdates in report one built successfully.
        assert len(updates) == 1

    def test_first_repo_updated(self):
        """ Test to ensure the first repo was updated. """

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[0]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status
