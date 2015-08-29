""" Test a valid yaml file is output. """

import os, yaml
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestYamlReport(object):
    """ Test a valid yaml file is output. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    @staticmethod
    def test_yaml_report():
        """ Test for the presence of the report.yaml file. """

        file_name = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml')
        assert os.path.isfile(file_name) == True

    @staticmethod
    def test_yaml_report_valid():
        """ Test for the vailidty of the yaml file. """

        file_name = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file_name)
        assert isinstance(data, dict) == True

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
