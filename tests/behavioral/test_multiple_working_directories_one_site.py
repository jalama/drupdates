""" Test one repo, multiple working directories. """

import os
from tests.behavioral.behavioral_utils import BehavioralUtils
from tests.behavioral.behavioral_utils import BehavioralException
from tests import Setup

class TestMultipleWorkingDirectoriesOneSite(BehavioralUtils):
    """ Test multiple working directories pass singleSite with one repoDict. """

    @classmethod
    def setup_class(cls):
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_repo_built(self):
        """ Test to ensure one repo built successfully. """

        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        # If 1 repo Siteupdates in report repo built successfully.
        assert len(updates) == 2

    def test_frst_repo_updated(self):
        """ Test to ensure the repo was updated. """

        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[0]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status
