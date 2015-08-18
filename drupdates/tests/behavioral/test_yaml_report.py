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
        """ Test for the presence of the resport.yaml file. """

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

        file_name = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file_name)
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        assert len(data[build_dir]) == 1

    @staticmethod
    def test_repo_updated():
        """ Test to ensure the repo was updated. """

        file_name = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file_name)
        status = "The following updates were applied"
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        result = data[build_dir]['drupal']['Siteupdate']['status'][0:35].strip()
        assert  result == status
