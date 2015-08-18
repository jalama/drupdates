""" Test passing workingDir on the CLI """

import os
from os.path import expanduser
from tests.behavioral.behavioral_utils import BehavioralUtils
from tests.behavioral.behavioral_utils import BehavioralException
from tests import Setup

class TestMultipleWorkingDirectoriesWorkingDirectoryCLI(BehavioralUtils):

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
        assert len(updates) == 1

    def test_frst_repo_updated(self):
        """ Test to ensure the repo was updated. """

        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[0]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status

    def test_working_dir(self):
        """ Test that the repo is in the correct working directory. """
        
        file = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file.readlines()
        path = os.path.join(self.test_directory, 'builds', 'test')
        path_index = results.index(path, -1)
        assert results[path_indx +1].strip()  == 'drupal'
