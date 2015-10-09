""" Parent class for behavioral tests, help build the test repos etc... """
import os, shutil, yaml, subprocess
from git import Repo
from os.path import expanduser
from os.path import basename
from drupdates.tests import Setup

class BehavioralException(Exception):
    'exception to demostrate fixture/test failures'
    pass

class BehavioralUtils(object):
    """ Parent class for behavioral tests, help build the test repos etc... """


    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.dirs = {'repos': {}, 'working' : {}}

    def build(self, test_file):
        """ Build the necessary directories. """

        settings = self.load_settings_files(test_file)
        working = {}
        # Build the source repos.
        for directory, attributes in settings['repo_dirs'].items():
            repo_directory = self.build_repo_dir(directory, attributes)
            if 'skip' in attributes and attributes['skip']:
                working_directory = attributes['working_directory']
                if working_directory not in working:
                    working[working_directory] = {}
                working[working_directory][directory] = repo_directory
        # Build the working directories in the test directory.
        working_directory = os.path.join(os.path.expanduser('~'), '.drupdates', 'builds')
        if os.path.isdir(working_directory):
            shutil.rmtree(working_directory)
        for directory, attributes in settings['working_dirs'].items():
            self.build_working_dir(directory, attributes, working)
        self.build_settings_file(settings)
        return self.run(settings)

    def load_settings_files(self, test_file):
        """ Load the test's settings file. """

        file_name = os.path.splitext(basename(test_file))[0]
        num = len(file_name) - 5
        file_name = "{0}.yaml".format(file_name[-num:])
        settings_file = os.path.join(self.current_dir, 'settings', file_name)
        try:
            default = open(settings_file, 'r')
        except IOError:
            raise BehavioralException
        settings = yaml.load(default)
        return settings

    def build_repo_dir(self, directory, settings):
        """ Build the test repo, delete it if it already exists. """

        base_directory = settings['base']
        target = os.path.join(self.test_directory, 'builds', directory)
        source = os.path.join(self.test_directory, 'builds', base_directory)
        if os.path.isdir(target):
            shutil.rmtree(target)
        Repo.clone_from(source, target, bare=True)
        if 'skip' in settings and not settings['skip'] or 'skip' not in settings:
            self.dirs['repos'][directory] = target
        return target

    def build_working_dir(self, directory, settings, working):
        """ Build a working directory. """

        working_directory = os.path.join(expanduser('~'), '.drupdates', settings['dir'])
        if not os.path.isdir(working_directory):
            os.makedirs(working_directory)
        self.dirs['working'][working_directory] = working_directory
        data = {}
        if 'custom_settings' in settings or directory in working:
            if 'custom_settings' in settings:
                data = settings['custom_settings']
            if directory in working and len(working[directory]):
                data['repoDict'] = {'value' : working[directory]}
            if len(data):
                BehavioralUtils.build_custom_setting(settings, data)

    @staticmethod
    def build_custom_setting(settings, data):
        """ If needed build custom setting for working directory. """

        working_directory = os.path.join(expanduser('~'), '.drupdates', settings['dir'])
        if not os.path.isdir(working_directory):
            os.makedirs(working_directory)
        os.chdir(working_directory)
        if not os.path.isdir('.drupdates'):
            os.makedirs('.drupdates')
        settings_file_directory = os.path.join(working_directory, '.drupdates')
        settings_file = "{0}/settings.yaml".format(settings_file_directory)
        with open(settings_file, 'w') as outfile:
            outfile.write(yaml.dump(data, default_flow_style=False))

    def build_settings_file(self, settings):
        """ Build settings file to ~/.drupdates/settings.yaml """

        drupdates_directory = os.path.join(expanduser('~'), '.drupdates')
        settings_file = "{0}/settings.yaml".format(drupdates_directory)
        if 'additional_settings' in settings:
            data = settings['additional_settings']
        else:
            data = {}
        # Add repoDict element to settings
        repos = {'value' : self.dirs['repos']}
        data['repoDict'] = repos
        # Add workingDir element to settings
        data['workingDir'] = {'value' : []}
        for directory in self.dirs['working']:
            data['workingDir']['value'].append(directory)
        with open(settings_file, 'w') as outfile:
            outfile.write(yaml.dump(data, default_flow_style=False))

    def run(self, settings):
        """ Run the drupdates command. """

        os.chdir(self.test_directory)
        commands = []
        # Parse options from the test's settings to be passed to Drupdates
        # via the CLI call.
        if 'options' in settings:
            for option, value in settings['options'].items():
                commands += ["--{0}={1}".format(option, value)]
        commands.insert(0, 'drupdates')
        outfile = open('results.txt', 'w')
        popen = subprocess.Popen(commands, stdout=outfile, stderr=subprocess.PIPE)
        results = popen.communicate()
        return results

    """ The following methods are used by test modules to analyze results."""

    @staticmethod
    def check_repo_updated(site, working_directory):
        """ Given a repo number check if it was updated. """

        file_name = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file_name)
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', working_directory)
        result = data[build_dir][site]['Siteupdate']['status']
        return result

    @staticmethod
    def count_repos_updated(working_directory):
        """ Count the number of repos updated. """

        file_name = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file_name)
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', working_directory)
        return len(data[build_dir])

    @staticmethod
    def count_sites_updated(site, working_directory):
        """ Count the number of sites that were updated in the repo. """

        file_name = open(os.path.join(os.path.expanduser('~'), '.drupdates', 'report.yaml'))
        data = yaml.load(file_name)
        build_dir = os.path.join(os.path.expanduser('~'), '.drupdates', working_directory)
        count = len(data[build_dir][site]['Siteupdate']['updates'])
        return count

    @staticmethod
    def get_dev_commit(site, working_directory):
        """ Return a git commit object. """

        file_name = open(os.path.join(expanduser('~'), '.drupdates', 'settings.yaml'), 'r')
        settings = yaml.load(file_name)
        working_dir = os.path.join(expanduser('~'), '.drupdates', working_directory)
        folder = os.path.join(working_dir, settings['repoDict']['value'][site])
        repo = Repo(folder)
        return repo.heads.dev.commit

    @staticmethod
    def get_drupdates_commit(site, working_directory):
        """ Return a git commit object. """

        file_name = open(os.path.join(expanduser('~'), '.drupdates', 'settings.yaml'), 'r')
        settings = yaml.load(file_name)
        working_dir = os.path.join(expanduser('~'), '.drupdates', working_directory)
        folder = os.path.join(working_dir, settings['repoDict']['value'][site])
        repo = Repo(folder)
        return repo.heads.drupdates.commit

    @staticmethod
    def count_commits(site, working_directory):
        """ Return number of commits in a repo. """

        file_name = open(os.path.join(expanduser('~'), '.drupdates', 'settings.yaml'), 'r')
        settings = yaml.load(file_name)
        working_dir = os.path.join(expanduser('~'), '.drupdates', working_directory)
        folder = os.path.join(working_dir, settings['repoDict']['value'][site])
        repo = Repo(folder)
        return len(list(repo.iter_commits('dev')))

    @staticmethod
    def count_modified_files(site, working_directory):
        """ Return a list of the modified files in the git index. """

        file_name = open(os.path.join(expanduser('~'), '.drupdates', 'settings.yaml'), 'r')
        settings = yaml.load(file_name)
        folder = os.path.join(settings['workingDir']['value'][0], site)
        repo = Repo(folder)
        return len(list(repo.git.ls_files('--modified')))
