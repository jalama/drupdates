""" Drupdates Site building module. """
import git, os, copy
from os.path import expanduser
from drupdates.utils import Utils
from drupdates.settings import Settings
from drupdates.settings import DrupdatesError
from drupdates.drush import Drush
from git import Repo

class DrupdatesBuildError(DrupdatesError):
    """ Parent Drupdates site build error. """

class Sitebuild(object):
    """ Build out the repository folder. """

    def __init__(self, site_name, ssh, working_dir):
        self.settings = Settings()
        self._site_name = site_name
        self.site_dir = os.path.join(working_dir, self._site_name)
        self.ssh = ssh
        self.utilities = Utils()
        self.si_files = copy.copy(self.settings.get('drushSiFiles'))

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
        self.utilities.load_dir_settings(self.site_dir)
        self.standup_site()
        try:
            repo_status = Drush.call(['st'], self._site_name, True)
        except DrupdatesError as st_error:
            raise DrupdatesBuildError(20, st_error.msg)
        finally:
            self.file_cleanup()
        if not 'bootstrap' in repo_status:
            msg = "{0} failed to Stand-up properly after running drush qd".format(self._site_name)
            raise DrupdatesBuildError(20, msg)
        self.utilities.sys_commands(self, 'postBuildCmds')
        return "Site build for {0} successful".format(self._site_name)

    def standup_site(self):
        """ Using the drush core-quick-drupal (qd) command stand-up a Drupal site.

        This will:
        - Perform site install with sqlite.
        - If needed, build webroot from a make file.
        - Install any sub sites (ie multi-sites)
        - Ensure that all the files in the web root are writable.

        """
        qd_settings = self.settings.get('qdCmds')
        qd_cmds = copy.copy(qd_settings)
        backup_dir = Utils.check_dir(self.settings.get('backupDir'))
        qd_cmds += ['--backup-dir=' + backup_dir]
        try:
            qd_cmds.remove('--no-backup')
        except ValueError:
            pass
        if self.settings.get('useMakeFile'):
            make_file = self.utilities.find_make_file(self._site_name, self.site_dir)
            if make_file:
                qd_cmds += ['--makefile=' + make_file]
            else:
                msg = "Can't find make file in {0} for {1}".format(self.site_dir, self._site_name)
                raise DrupdatesBuildError(20, msg)
            if self.settings.get('buildSource') == 'make':
                qd_cmds.remove('--use-existing')
        try:
            Drush.call(qd_cmds, self._site_name)
            sub_sites = Drush.get_sub_site_aliases(self._site_name)
            for alias, data in sub_sites.items():
                Drush.call(qd_cmds, alias)
                # Add sub site settings.php to list of file_cleanup() files.
                sub_site_st = Drush.call(['st'], alias, True)
                self.si_files.append(sub_site_st['site'] + '/settings.php')
                self.si_files.append(sub_site_st['files'] + '/.htaccess')
                self.si_files.append(sub_site_st['site'])
        except DrupdatesError as standup_error:
            raise standup_error

    def file_cleanup(self):
        """ Drush sets the folder permissions for some file to be 0444, convert to 0777. """
        drush_dd = Drush.call(['dd', '@drupdates.' + self._site_name])
        site_webroot = drush_dd[0]
        for name in self.si_files:
            complete_name = os.path.join(site_webroot, name)
            if os.path.isfile(complete_name) or os.path.isdir(complete_name):
                try:
                    os.chmod(complete_name, 0o777)
                except OSError:
                    msg = "Couldn't change file permission for {0}".format(complete_name)
                    raise DrupdatesBuildError(20, msg)
