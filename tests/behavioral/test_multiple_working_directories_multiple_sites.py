""" Test running Drupdates on multiple repos, multiple working Directories. """

"""
    note: The second working directory will have it's own settings file.
"""
import os
from os.path import expanduser
from tests.behavioral.behavioral_utils import BehavioralUtils
from tests.behavioral.behavioral_utils import BehavioralException
from tests import Setup

class TestMultipleWorkingDirectoriesMultipleSites(BehavioralUtils):

    @classmethod
    def setup_class(cls):
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_repo_built(self):
        """ Test to ensure both repos built successfully. """

        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        """ If 2 repo Siteupdates in report repo built successfully. """
        assert len(updates) == 2

    def test_frst_repo_updated(self):
        """ Test to ensure the repo was updated. """

        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[0]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status

    def test_second_repo_updated(self):
        """ Test to ensure the second repo was updated. """

        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[1]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status
