""" Parent class for behavioral tests, help build the test repos etc... """
import os, shutil, yaml, subprocess
from nose.tools import *
from git import Repo
from os.path import expanduser
from os.path import basename
from tests import Setup

class BehavioralException(Exception):
    'exception to demostrate fixture/test failures'
    pass

class BehavioralUtils(object):

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir
        self.working_directory = ""
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.repos = {}

    def build(self, test_file):
        """ Open test's setting files and build the necessary directories. """
        file_name = os.path.splitext(basename(test_file))[0]
        num = len(file_name) - 5
        file_name = "{0}.yaml".format(file_name[-num:])
        settings_file = os.path.join(self.current_dir, 'settings', file_name)
        try:
            default = open(settings_file, 'r')
        except IOError as error:
            msg = "Can't open or read settings file, {0}".format(settings_file)
            raise BehavioralException
        settings = yaml.load(default)
        for directory, attributes in settings['repo_dirs'].iteritems():
            repo_directory = self.build_repo_dir(directory, attributes)
            if 'custom_settings' in attributes:
                self.build_custom_setting(attributes['custom_settings'])
            self.repos[directory] = repo_directory
        self.build_settings_file(settings)
        return self.run(settings)

    def build_repo_dir(self, directory, settings):
        """ Build the test repo. """

        if 'working_directory' in settings:
            working = settings['working_directory']
        else:
            working = 'builds'
        self.build_working_dir(working)
        base_directory = settings['base']
        target = os.path.join(self.working_directory, directory)
        source = os.path.join(self.test_directory, 'builds', base_directory)
        if os.path.isdir(target):
            shutil.rmtree(target)
        Repo.clone_from(source, target, bare = True)
        return target

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

    def build_settings_file(self, settings):
        """ Build settings file to ~/.drupdates/settings.yaml """

        drupdates_directory = os.path.join(expanduser('~'), '.drupdates')
        settings_file = "{0}/settings.yaml".format(drupdates_directory)
        repos = {'value' : self.repos}
        if 'additional_settings' in settings:
            data = settings['additional_settings']
        else:
            data = {}
        data['repoDict'] = repos
        with open(settings_file, 'w') as outfile:
            outfile.write( yaml.dump(data, default_flow_style=False) )

    def run(self, settings):
        os.chdir(self.test_directory)
        commands = []
        if 'options' in settings:
            for option, value in settings['options']:
                commands += ["{0}={1}".format(option, value)]
        commands.insert(0, 'drupdates')
        outfile = open('results.txt','w')
        popen = subprocess.Popen(commands, stdout=outfile, stderr=subprocess.PIPE)
        results = popen.communicate()

    @staticmethod
    def list_duplicates_of(seq, item):
        start_at = -1
        locs = []
        while True:
            try:
                loc = seq.index(item, start_at+1)
            except ValueError:
                break
            else:
                locs.append(loc)
                start_at = loc
        return locs
