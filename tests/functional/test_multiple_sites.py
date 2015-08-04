""" Test running Drupdates on multiple sites. """
from __future__ import print_function
import os, yaml
from os.path import basename
from tests.functional.functional_utils import FunctionalUtils
from tests.functional.functional_utils import FunctionalException

class TestMultipleSites(object):

    @classmethod
    def setup_class(cls):
        # print "setup"
        current_dir = os.path.dirname(os.path.realpath(__file__))
        utils = FunctionalUtils()
        file_name = os.path.splitext(basename(__file__))[0]
        num = len(file_name) - 5
        file_name = "{0}.yaml".format(file_name[-num:])
        settings_file = os.path.join(current_dir, 'settings', file_name)
        try:
            default = open(settings_file, 'r')
        except IOError as error:
            msg = "Can't open or read settings file, {0}".format(settings_file)
            raise FunctionalException
        settings = yaml.load(default)
        utils.build(settings)

    @classmethod
    def teardown_class(cls):
        pass

    def test_method_1(self):
        print(__name__, ': TestClass.test_method_1()')
