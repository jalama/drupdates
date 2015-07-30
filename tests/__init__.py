from nose.tools import *
import drupdates, git, os, shutil
from os.path import expanduser

def setup_package():
    setup_tests = Setup()
    setup_tests.build_directory()

def teardown_package():
    setup_tests = Setup()
    setup_tests.destroy_directory()

class Setup(object):
    """ Set-up the basic test repos for other tests to clone and run. """

    def __init__(self):
        self.test_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'testing')

    def build_directory(self):
        if not os.path.isdir(self.test_dir):
            os.makedirs(self.test_dir)

    def destroy_directory(self):
        shutil.rmtree(self.test_dir)

    def build_base_repository(self, drupal_version, make_format, destination_folder):
        folder = os.path.join(self.test_dir, destination_folder)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        # TODO: need to choose between built by hand or making using drush make
        makefile = "drupal{0}_drupdates.{1}".format(drupal_version, make_format)
