""" Parent class for functional tests, help build the test repos etc... """
import os, shutil
from nose.tools import *
from git import Repo
from os.path import expanduser

class FunctionalTests(object):

    def __init__(self):
        # TODO: ideally this is pull form Setup() class in __init__.py
        self.test_directory = os.path.join(os.path.expanduser('~'), '.drupdates', 'testing')
        self.working_directory = ""
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    def build(self, settings):
        """ Build out the directories for a test. """

        for directory, attributes in settings['repo_dirs']:
            self.build_repo_dir(direcotry, attributes)
            if custom_settings in attributes:
                self.build_custom_setting(attributes['custom_settings'])
        if settings_fil not in settings:
            drupdates_settings = 'drupal'
        else:
            drupdates_settings = settings['settings_file']
        self.build_settings_file(drupdates_settings)

    def build_repo_dir(self, directory, settings):
        """ Build the test repo. """

        if not working_directory in settings:
            working = 'builds'
        else:
            working = settings['working_directory']
        working_directory = self.build_working_dir(working)
        base_directory = settings['base']
        target = os.path.join(working_directory, directory)
        source = os.path.join(self.test_directory, 'builds', base_directory)
        if os.path.isdir(target):
            shutil.rmtree(target)
        Repo.clone_from(source, target)

    def build_working_dir(self, directory):
        """ Build the working directory. """

        working_directory = os.path.join(self.test_directory, directory)
        if not os.path.isdir(working_directory):
            os.makedirs(working_directory)
        self.working_directory = working_directory

    def build_custom_setting(self, settings_file):
        """ If needed build custom setting for working dir. """

        os.chdir(self.working_directory)
        settings_source = os.path.join(self.current_dir, 'settings', settings_file)
        if not os.path.isdir('.drupdates'):
            os.makedirs('.drupdates')
        target_directory = os.path.join(self.working_directory, '.drupdates')
        target = "{0}/settings.yaml".format(target_directory)
        shutil.copyfile(settings_source, target)

    def build_settings_file(self, settings_file):
        """ Copy settings file to ~/.drupdates/settings.yaml """

        settings_source = os.path.join(self.current_dir, 'settings', settings_file)
        drupdates_directory = os.path.join(expanduser('~'), '.drupdates')
        target = "{0}/settings.yaml".format(drupdates_directory)
        shutil.copyfile(settings_source, target)
