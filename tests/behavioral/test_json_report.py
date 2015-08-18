""" Test a valid json file is output. """
import os, json
from tests.behavioral.behavioral_utils import BehavioralUtils
from tests.behavioral.behavioral_utils import BehavioralException
from tests import Setup

class TestJsonReport(BehavioralUtils):

    @classmethod
    def setup_class(cls):
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_json_report(self):
        """ Test for the presence of the resport.json file. """

        file = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.json')
        assert os.path.isfile(file) == True

    def test_json_report_valid(self):
        """ Test for the vailidty of the json file. """

        file = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.json')
        with open(file) as data_file:
            data = json.load(data_file)
        assert isinstance(data, dict) == True

    def test_repo_built(self):
        """ Test to ensure one repo built successfully. """

        file = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.json')
        with open(file) as data_file:
            data = json.load(data_file)
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        assert len(data[build_dir]) == 1

    def test_repo_updated(self):
        """ Test to ensure the repo was updated. """

        file = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.json')
        with open(file) as data_file:
            data = json.load(data_file)
        status = "The following updates were applied"
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        result = data[build_dir]['drupal']['Siteupdate']['status'][0:35].strip()
        assert  result == status
