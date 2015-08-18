""" Test Multiple repos, multiple working directories, passing singleSite. """

"""
    note: Both sites should get updated as singleSite won't work with multiple
    working directories.
"""
import os
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestMultipleWorkingDirectoriesSingleSites(object):
    """ Test multiple repos, multiple working directories, pass singleSite. """

    @classmethod
    def setup_class(cls):
        """ Setup test class."""
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_repo_built(self):
        """ Test to ensure both repos built successfully. """

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        # If 2 repo Siteupdates in report repo built successfully.
        assert len(updates) == 2

    def test_frst_repo_updated(self):
        """ Test to ensure the repo was updated. """

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
