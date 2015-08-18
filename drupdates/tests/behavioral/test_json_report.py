""" Test a valid json file is output. """
import os, json
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestJsonReport(object):
    """ Test a valid json file is output. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    @staticmethod
    def test_json_report():
        """ Test for the presence of the resport.json file. """

        file_name = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.json')
        assert os.path.isfile(file_name) == True

    @staticmethod
    def test_json_report_valid():
        """ Test for the vailidty of the json file. """

        file_name = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.json')
        with open(file_name) as data_file:
            data = json.load(data_file)
        assert isinstance(data, dict) == True

    @staticmethod
    def test_repo_built():
        """ Test to ensure one repo built successfully. """

        file_name = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.json')
        with open(file_name) as data_file:
            data = json.load(data_file)
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        assert len(data[build_dir]) == 1

    @staticmethod
    def test_repo_updated():
        """ Test to ensure the repo was updated. """

        file_name = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.json')
        with open(file_name) as data_file:
            data = json.load(data_file)
        status = "The following updates were applied"
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        result = data[build_dir]['drupal']['Siteupdate']['status'][0:35].strip()
        assert  result == status
