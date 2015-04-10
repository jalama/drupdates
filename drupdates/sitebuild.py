""" Drupdates Site building module. """
import git, os, subprocess
from drupdates.utils import Utils
from drupdates.settings import Settings
from drupdates.settings import DrupdatesError
from drupdates.drush import Drush
from drupdates.constructors.datastores import Datastores
from git import Repo

class DrupdatesBuildError(DrupdatesError):
    """ Parent Drupdates site build error. """

class DrupdatesImportError(DrupdatesError):
    """ Error importing back-up database. """

class DrupdatesConstructError(DrupdatesError):
    """ Error importing back-up database. """

class Sitebuild(object):
    """ Build out the repository folder. """

    def __init__(self, siteName, ssh, working_dir):
        self.settings = Settings()
        self._site_name = siteName
        self.site_dir = os.path.join(working_dir, self._site_name)
        self.ssh = ssh
        self.utilities = Utils()

    def build(self):
        """ Core build method. """
        working_branch = self.settings.get('workingBranch')
        try:
            Utils.remove_dir(self.site_dir)
        except DrupdatesError as remove_error:
            raise DrupdatesBuildError(20, remove_error.msg)
        self.utilities.sys_commands(self, 'preBuildCmds')
        repository = Repo.init(self.site_dir)
        remote = git.Remote.create(repository, self._site_name, self.ssh)
        try:
            remote.fetch(working_branch)
        except git.exc.GitCommandError as error:
            msg = "{0}: Could not checkout {1}. \n".format(self._site_name, working_branch)
            msg += "Error: {0}".format(error)
            raise DrupdatesBuildError(20, msg)
        git_repo = repository.git
        git_repo.checkout('FETCH_HEAD', b=working_branch)
        if self.settings.get('useMakeFile'):
            self.utilities.make_site(self._site_name, self.site_dir)
        st_cmds = ['st']
        repo_status = Drush.call(st_cmds, self._site_name, True)
        if not isinstance(repo_status, dict):
            msg = "{0} failed to respond to drush status".format(self._site_name)
            raise DrupdatesBuildError(20, msg)
        # If this is not a Drupal repo move to the next repo
        if not 'drupal-version' in repo_status:
            msg = "{0}, from drush pm-status: this isn't a drupal site".format(self._site_name)
            raise DrupdatesBuildError(20, msg)
        if not 'bootstrap' in repo_status:
            # Re-build database if it fails go to the next repo
            if 'site' in repo_status:
                site = os.path.basename(repo_status['site'])
            else:
                site = 'default'
            try:
                self.construct_site(site)
            except DrupdatesError as construct_error:
                raise construct_error
        if self.settings.get('importBackup'):
            # Import the backup file
            try:
                self.import_backup()
            except DrupdatesError as import_error:
                raise import_error
        self.utilities.sys_commands(self, 'postBuildCmds')
        ret = "Site build for {0} successful".format(self._site_name)
        return ret

    def construct_site(self, site='default'):
        """ Rebulid the Drupal site: build DB, settings.php, etc..."""
        Datastores().build(self._site_name)
        # Perform Drush site-install to get a base settings.php file
        si_cmds = ['si', 'minimal', '-y', '--sites-subdir=' + site]
        try:
            Drush.call(si_cmds, self._site_name)
        except DrupdatesError as install_error:
            msg = "Drush site install (si) failed.\n"
            msg += "Drush output {0}".format(install_error.msg)
            raise DrupdatesConstructError(30, msg)
        st_cmds = ['st']
        repo_status = Drush.call(st_cmds, self._site_name, True)
        if not 'bootstrap' in repo_status:
            msg = "Bootstrap failed after site install for {0}".format(self._site_name)
            raise DrupdatesConstructError(20, msg)
        drush_dd = Drush.call(['dd', '@drupdates.' + self._site_name])
        site_webroot = drush_dd[0]
        si_files = self.settings.get('drushSiFiles')
        for name in si_files:
            complete_name = os.path.join(site_webroot, name)
            if os.path.isfile(complete_name) or os.path.isdir(complete_name):
                try:
                    os.chmod(complete_name, 0777)
                except OSError:
                    msg = "Couldn't change file permission for {0}".format(complete_name)
                    raise DrupdatesConstructError(20, msg)

    def import_backup(self):
        """ Import a SQL dump using drush sqlc.

        alias -- A Drush alias

        """
        alias = self._site_name
        backport_dir = self.settings.get('backupDir')
        if os.path.isfile(backport_dir + alias + '.sql'):
            commands = ['drush', '@drupdates.' + alias, 'sqlc']
            popen = subprocess.Popen(commands, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            results = popen.communicate(file(backport_dir + alias + '.sql').read())
            if results[1]:
                msg = "{0} DB import error: {1}".format(alias, results[1])
                raise DrupdatesImportError(20, msg)
        else:
            msg = "{0} could not find backup file, skipping import".format(alias)
            raise DrupdatesImportError(20, msg)
