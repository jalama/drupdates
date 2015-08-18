""" Test a valid yaml file is output. """
import os, yaml
from tests.behavioral.behavioral_utils import BehavioralUtils
from tests.behavioral.behavioral_utils import BehavioralException
from tests import Setup

class TestYamlReport(BehavioralUtils):

    @classmethod
    def setup_class(cls):
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_yaml_report(self):
        """ Test for the presence of the resport.yaml file. """

        file = os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml')
        assert os.path.isfile(file) == True

    def test_yaml_report_valid(self):
        """ Test for the vailidty of the yaml file. """

        file = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file)
        assert isinstance(data, dict) == True

    def test_repo_built(self):
        """ Test to ensure one repo built successfully. """

        file = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file)
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        assert len(data[build_dir]) == 1

    def test_repo_updated(self):
        """ Test to ensure the repo was updated. """

        file = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file)
        status = "The following updates were applied"
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        result = data[build_dir]['drupal']['Siteupdate']['status'][0:35].strip()
        assert  result == status
