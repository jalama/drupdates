""" Test a repo that contains symlinks, ensure they are still in place after run. """

import yaml, os
from os.path import expanduser
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestSimpleWithSymlinks(object):
    """ Test running Drupdates on one repo that contains symlinks to be retained. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir
        self.utils = BehavioralUtils()

    @staticmethod
    def test_repo_built():
        """ Test to ensure one repo built successfully. """

        count = BehavioralUtils.count_repos_updated('builds')
        # If 1 repo Siteupdates in report repo built successfully.
        assert count == 1

    @staticmethod
    def test_repo_updated():
        """ Test to ensure the repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated('drupal', 'builds')
        assert report_status == status

    @staticmethod
    def test_symlink_presence():
        """ Test to make sure the sites/example.com/modules symlink exists. """

        file_name = open(os.path.join(expanduser('~'), '.drupdates', 'settings.yaml'), 'r')
        settings = yaml.load(file_name)
        folder = os.path.join(settings['workingDir']['value'][0], 'drupal', 'sites', 'example.com')
        assert os.path.islink(os.path.join(folder, 'modules'))
