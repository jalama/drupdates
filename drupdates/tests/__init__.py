""" Build the base repos testing repos are cloned from. """
import drupdates, git, os, shutil, yaml, glob, nose, subprocess
from os.path import expanduser
from git import Repo
from drupdates.drush import Drush
from drupdates.settings import DrupdatesError

def setup_package():
    """ Setup the basic base repos and base directory. """
    setup_tests = Setup()
    setup_tests.build_directory()
    setup_tests.build_base_repos()

def teardown_package():
    """ Teardown the testing directory. """
    setup_tests = Setup()
    setup_tests.destroy_directory()

class Setup(object):
    """ Set-up the basic test repos for other tests to clone and run. """

    def __init__(self):
        self.test_dir = os.path.join(os.path.expanduser('~'), '.drupdates', 'testing')
        self.make_file = ''
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    def build_directory(self):
        """ Build the base testing directory. """

        if not os.path.isdir(self.test_dir):
            os.makedirs(self.test_dir)

        files = []
        directory = os.path.join(expanduser('~'), '.drupdates')
        files.append(os.path.join(directory, 'settings.yaml'))
        files.append(os.path.join(directory, 'report.yaml'))
        files.append(os.path.join(directory, 'report.json'))
        files.append(os.path.join(directory, 'drupdates.debug'))
        files.append(os.path.join(expanduser('~'), '.drush', 'drupdates.aliases.drushrc.php'))

        for file_name in files:
            if os.path.isfile(file_name):
                os.remove(file_name)

    def destroy_directory(self):
        """ Destroy base testing directory and remove base settings file. """

        shutil.rmtree(self.test_dir)

    def build_base_repos(self):
        """ Build out the base repo used by the functional tests. """

        directory_list = open(os.path.join(self.current_dir, 'base_dirs.yaml'))
        base_directory_list = yaml.load(directory_list)
        for directory, options in base_directory_list['dirs'].items():
            self.get_make_file(options['version'], options['make_format'])
            base_directory = self.build_base_directory(directory)
            if not base_directory:
                continue
            if not options['build'] or 'subfolder' in options:
                make_file_name = "{0}.{1}".format(options['make_file'], options['make_format'])
                self.copy_make_file(make_file_name, base_directory)
                path = base_directory
            if options['build']:
                subfolder = ''
                if 'subfolder' in options:
                    subfolder = options['subfolder']
                path = self.run_drush_make(base_directory, subfolder)
            if 'commands' in options:
                os.chdir(path)
                for commands in options['commands']:
                    popen = subprocess.Popen(commands,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
                    popen.communicate()
            if 'sites' in options:
                for site in options['sites']:
                    destination = "--contrib-destination=sites/{0}.com".format(site)
                    add_cmds = [destination, '--no-core']
                    self.make_file = os.path.join(self.current_dir,
                                                  'makefiles',
                                                  "{0}.yaml".format(site))
                    self.run_drush_make(base_directory, subfolder, add_cmds)
            if 'custom_settings' in options:
                settings_file_directory = os.path.join(path, '.drupdates')
                settings_file = "{0}/settings.yaml".format(settings_file_directory)
                with open(settings_file, 'w') as outfile:
                    outfile.write(yaml.dump(options['custom_settings'], default_flow_style=False))
            Setup.make_git_repo(base_directory)

    def build_base_directory(self, target_directory):
        """ Build the empty base directory. """

        folder = os.path.join(self.test_dir, 'builds', target_directory)
        if not os.path.isdir(folder):
            os.makedirs(folder)
            return folder
        else:
            return ""

    def get_make_file(self, drupal_version, make_format):
        """ Get the name and location of Drush Make file to build base repo. """

        makefile = "drupal{0}.{1}".format(drupal_version, make_format)
        self.make_file = os.path.join(self.current_dir, 'makefiles', makefile)

    def copy_make_file(self, target_file, target_directory):
        """ Copy target_file to target_directory. """

        make_file_path = os.path.join(target_directory, target_file)
        shutil.copyfile(self.make_file, make_file_path)

    def run_drush_make(self, target_directory, subfolder, add_cmds=None):
        """ Run drush make to build the base repo. """

        path = os.path.join(target_directory, subfolder)
        cmds = ['make', self.make_file, path]
        if add_cmds and isinstance(add_cmds, list):
            cmds += add_cmds
        else:
            if os.path.isdir(path):
                shutil.rmtree(path)
        try:
            Drush.call(cmds)
        except DrupdatesError as error:
            print(error.msg)
        return path

    @staticmethod
    def make_git_repo(directory):
        """ Make the repo folder a git repo. """

        repo = Repo.init(directory)
        index = repo.index
        files = repo.untracked_files
        index.add(files)
        index.commit('Initial Commit')
        repo.heads.master.checkout(b='dev')
        repo.heads.master.checkout()
