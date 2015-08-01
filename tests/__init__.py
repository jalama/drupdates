""" Build the base repos testing repos are cloned from. """
from nose.tools import *
import drupdates, git, os, shutil, yaml, glob
from os.path import expanduser
from git import Repo
from drupdates.drush import Drush
from drupdates.settings import DrupdatesError

def setup_package():
    setup_tests = Setup()
    setup_tests.build_directory()
    setup_tests.build_base_repos()

def teardown_package():
    setup_tests = Setup()
    setup_tests.destroy_directory()

class Setup(object):
    """ Set-up the basic test repos for other tests to clone and run. """

    def __init__(self):
        self.test_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'testing')
        self.make_file = ''
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    def build_directory(self):
        if not os.path.isdir(self.test_dir):
            os.makedirs(self.test_dir)

    def destroy_directory(self):
        shutil.rmtree(self.test_dir)

    def build_base_repos(self):
        """ Build out the base repo used by the functional tests. """

        directory_list = open(os.path.join(self.current_dir, 'base_dirs.yaml'))
        base_directory_list = yaml.load(directory_list)
        for directory, options in base_directory_list['dirs'].iteritems():
            self.get_make_file(options['version'], options['make_format'])
            base_directory = self.build_base_directory(directory)
            if not options['build'] or 'subfolder' in options:
                make_file_name = "{0}.{1}".format(options['make_file'], options['make_format'])
                self.copy_make_file(make_file_name, base_directory)
            if options['build']:
                if 'subfolder' in options:
                    subfolder = options['subfolder']
                else:
                    subfolder = ''
                self.run_drush_make(base_directory, subfolder)
            self.build_repo(base_directory)

    def build_base_directory(self, target_directory):
        """ Build the empty base directory. """

        folder = os.path.join(self.test_dir, 'builds', target_directory)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return folder

    def get_make_file(self, drupal_version, make_format):
        """ Get the name and location of Drush Make file to build base repo. """

        makefile = "drupal{0}_drupdates.{1}".format(drupal_version, make_format)
        self.make_file = os.path.join(self.current_dir, 'makefiles', makefile)

    def copy_make_file(self, target_file, target_directory):
        """ Copy target_file to target_directory. """

        make_file_path = os.path.join(target_directory, target_file)
        shutil.copyfile(self.make_file, make_file_path)

    def run_drush_make(self, target_directory, subfolder):
        """ Run drush make to build the base repo. """

        path = os.path.join(target_directory, subfolder)
        cmds = ['make', self.make_file, path]
        if os.path.isdir(path):
            shutil.rmtree(path)
        try:
            Drush.call(cmds)
        except DrupdatesError as e:
            print e.msg

    def build_repo(self, directory):
        """ Build the repo as a bare repository. """
        repo = Repo.init(directory)
        index = repo.index
        files = repo.untracked_files
        index.add(files)
        index.commit('Initial Commit')
        repo.heads.master.checkout(b='dev')
        repo.heads.master.checkout()
