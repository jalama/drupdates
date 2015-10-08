""" Primary Drupdates Module. """
import os, shutil, yaml, sys
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
        self.utilities = Utils()
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
            Utils.check_dir(directory)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        src = os.path.join(current_dir, "templates/settings.template")
        settings_file = os.path.join(Utils.check_dir(base_dir), 'settings.yaml')
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
            self.utilities.write_debug_file()
        report = {}
        for current_working_dir in self.working_dirs:
            try:
                current_working_dir = Utils.check_dir(current_working_dir)
                self.utilities.load_dir_settings(current_working_dir)
                update = self.update_sites(current_working_dir)
                report[current_working_dir] = update
            except DrupdatesError as update_error:
                report[current_working_dir] = update_error.msg
                if update_error.level >= 30:
                    break
                else:
                    continue
        try:
            reporting = Reports()
        except DrupdatesError as reports_error:
            print("Reporting error: \n {0}".format(reports_error.msg))
            sys.exit(1)
        reporting.send(report)

    def update_sites(self, working_dir):
        """ Run updates for a working directory's sites. """
        report = {}
        self.aliases(working_dir)
        blacklist = self.settings.get('blacklist')
        sites = Repos().get()
        if self.single_site:
            sites = {self.single_site : sites[self.single_site]}
        for site_name, ssh in sites.items():
            if self.settings.get('verbose'):
                msg = "Drupdates is working on the site: {0} ...".format(site_name)
                print(msg)
            report[site_name] = {}
            if site_name in blacklist:
                continue
            self.utilities.load_dir_settings(working_dir)
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
        filepath.write(template.safe_substitute(path=working_dir,
                                                webroot=webroot_dir))

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
