""" Test running Drupdates on multiple sites. """
from __future__ import print_function
import os
from tests.behavioral.behavioral_utils import BehavioralUtils
from tests.behavioral.behavioral_utils import BehavioralException
from tests import Setup

class TestMultipleSiteOptionSingleSite(BehavioralUtils):

    @classmethod
    def setup_class(cls):
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_all_repos_built(self):
        """ Test to ensure all three repos built successfully. """

        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        """ If 3 repos have Siteupdates in report three built successfully. """
        assert len(updates) == 1

    def test_first_repo_updated(self):
        """ Test to ensure the first repo was updated. """

        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[0]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status
