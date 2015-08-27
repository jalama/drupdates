""" Test passing workingDir on the CLI """

import os, yaml
from os.path import expanduser
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestMultipleWorkingDirectoriesWorkingDirectoryCLI(object):
    """ Test passing workingDir on the CLI """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    @staticmethod
    def test_repo_built():
        """ Test to ensure both repos built successfully. """

        count = BehavioralUtils.count_repos_updated('builds/test')
        # If 1 repo Siteupdates in report repo built successfully.
        assert count == 1

    @staticmethod
    def test_frst_repo_updated():
        """ Test to ensure the repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated('drupal', 'builds/test')
        assert report_status == status

    @staticmethod
    def test_working_dir():
        """ Test that the repo is in the correct working directory. """

        file_name = open(os.path.join(expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file_name)
        build_dir = os.path.join(expanduser('~'), '.drupdates', 'builds', 'test')
        assert 'drupal' in data[build_dir]
