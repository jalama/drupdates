""" Primary Drupdates Module. """
import os, shutil, yaml, sys, pip
from os.path import expanduser
from string import Template
from drupdates.utils import Utils
from drupdates.settings import Settings
from drupdates.settings import DrupdatesError
from drupdates.constructors.repos import Repos
from drupdates.constructors.reports import Reports

class Updates(object):
    """ Run through the working directories and sites updating them. """

    def __init__(self):
        self.settings = Settings()
        self.install()
        self.working_dirs = self.settings.get('workingDir')
        self.single_site = ''
        self.alias_file = None
        if isinstance(self.working_dirs, str):
            self.working_dirs = [self.working_dirs]
        # by design, SingleSite setting only works with single working directory
        if len(self.working_dirs) == 1:
            self.single_site = self.settings.get('singleSite')

    def install(self):
        """ Basic Installation of Drupdates. """
        base_dir = self.settings.get('baseDir')
        backup_dir = self.settings.get('backupDir')
        dirs = [backup_dir, base_dir]
        for directory in dirs:
            Updates.check_dir(directory)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        src = os.path.join(current_dir, "templates/settings.template")
        settings_file = os.path.join(Updates.check_dir(base_dir), 'settings.yaml')
        instructions_url = "http://drupdates.readthedocs.org/en/latest/setup/"
        if not os.path.isfile(settings_file):
            shutil.copy(src, settings_file)
            msg = "The Settings file {0} was created and needs updated.\n".format(settings_file)
            msg += "See {0} for instructions".format(instructions_url)
            print(msg)
            sys.exit(1)
        current_settings = open(settings_file, 'r')
        settings = yaml.load(current_settings)
        if 'repoDict' in settings and 'example' in settings['repoDict']['value']:
            msg = "The default Settings file, {0}, needs updated. \n ".format(settings_file)
            msg += "See {0} for instructions".format(instructions_url)
            print(msg)
            sys.exit(1)

    def run_updates(self):
        """ Drupdates main function. """
        if self.settings.get('debug'):
            self.write_debug_file()
        report = {}
        for current_working_dir in self.working_dirs:
            try:
                current_working_dir = Updates.check_dir(current_working_dir)
                self.working_dir_settings(current_working_dir)
                update = self.update_site(current_working_dir)
                report[current_working_dir] = update
            except DrupdatesError as update_error:
                report[current_working_dir] = update_error.msg
                if update_error.level >= 30:
                    break
                else:
                    continue
        reporting = Reports()
        reporting.send(report)

    def update_site(self, working_dir):
        """ Run updates for an individual working directory. """
        report = {}
        self.aliases(working_dir)
        blacklist = self.settings.get('blacklist')
        sites = Repos().get()
        if self.single_site:
            sites = {self.single_site : sites[self.single_site]}
        for site_name, ssh in sites.items():
            report[site_name] = {}
            if site_name in blacklist:
                continue
            for phase in self.settings.get("drupdatesPhases"):
                mod = __import__('drupdates.' + phase['name'].lower(), fromlist=[phase])
                class_ = getattr(mod, phase['name'])
                instance = class_(site_name, ssh, working_dir)
                result = ''
                try:
                    call = getattr(instance, phase['method'])
                    result = call()
                except DrupdatesError as error:
                    result = error.msg
                    if error.level < 30:
                        break
                    if error.level >= 30:
                        msg = "Drupdates: fatal error\n Drupdates returned: {0}".format(result)
                        raise DrupdatesError(error.level, msg)
                finally:
                    report[site_name][phase['name']] = result

        self.settings.reset()
        self.delete_files()
        return report

    @staticmethod
    def check_dir(directory):
        """ Ensure the directory is writable. """
        directory = Utils.detect_home_dir(directory)
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError as error:
                msg = 'Unable to create non-existant directory {0} \n'.format(directory)
                msg += 'Error: {0}\n'.format(error.strerror)
                msg += 'Moving to next working directory, if applicable'
                raise DrupdatesError(20, msg)
        filepath = os.path.join(directory, "text.txt")
        try:
            open(filepath, "w")
        except IOError:
            msg = 'Unable to write to directory {0} \n'.format(directory)
            raise DrupdatesError(20, msg)
        os.remove(filepath)
        return directory

    def working_dir_settings(self, working_dir):
        """ Add custom settings for the working direcotry. """
        working_settings = os.path.join(working_dir, '.drupdates/settings.yaml')
        if os.path.isfile(working_settings):
            self.settings.add(working_settings, True)

    def aliases(self, working_dir):
        """ Build a Drush alias file in $HOME/.drush, with alises to be used later.

        Notes:
        The file name is controlled by the drushAliasFile settings
        All of the aliases will be prefixed with "drupdates" if the default file name
        is retained
        """

        alias_file_name = self.settings.get('drushAliasFile')
        drush_folder = os.path.join(expanduser('~'), '.drush')
        self.alias_file = os.path.join(drush_folder, alias_file_name)
        if not os.path.isdir(drush_folder):
            try:
                os.makedirs(drush_folder)
            except OSError as error:
                msg = "Could not create ~/.drush folder \n Error: {0}".format(error.strerror)
                raise DrupdatesError(30, msg)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Symlink the Drush aliases file
        src = os.path.join(current_dir, "templates/aliases.template")
        doc = open(src)
        template = Template(doc.read())
        doc.close()
        try:
            filepath = open(self.alias_file, 'w')
        except OSError as error:
            msg = "Could not create {0} file\n Error: {1}".format(self.alias_file, error.strerror)
            raise DrupdatesError(30, msg)
        webroot_dir = self.settings.get('webrootDir')
        host_set = self.settings.get('datastoreHost')
        driver_set = self.settings.get('datastoreDriver')
        port_set = self.settings.get('datastorePort')
        filepath.write(template.safe_substitute(host=host_set, driver=driver_set,
                                                path=working_dir, webroot=webroot_dir,
                                                port=port_set))

        filepath.close()

    def delete_files(self):
        """ Clean up files used by Drupdates. """
        if os.path.isfile(self.alias_file):
            try:
                os.remove(self.alias_file)
            except OSError as error:
                msg = "Clean-up error, couldn't remove {0}\n".format(self.alias_file)
                msg += "Error: {1}".format(error.strerror)
                print(msg)
        return True

    def write_debug_file(self):
        """ Write debug file for this run.

        Write file containing your system settings to be used to record python
        and Drupdates state at the time Drupdates was run.
        """

        base_dir = self.settings.get('baseDir')
        directory = self.check_dir(base_dir)
        debug_file_name = os.path.join(directory, 'drupdates.debug')
        debug_file = open(debug_file_name, 'w')
        debug_file.write("Python Version:\n")
        python_version = "{0}\n\n".format(sys.version)
        debug_file.write(python_version)
        installed_packages = pip.get_installed_distributions()
        if len(installed_packages):
            debug_file.write("Installed Packages:\n\n")
            for i in installed_packages:
                package = "{0}\n".format(str(i))
                debug_file.write(package)
        settings = self.settings.list()
        debug_file.write("\nDrupdates Settings:\n\n")
        for name, setting in settings.items():
            line = "{0} : {1}\n".format(name, str(setting['value']))
            debug_file.write(line)
