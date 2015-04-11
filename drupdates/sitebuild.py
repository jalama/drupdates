""" Drupdates Site building module. """
import git, os
from drupdates.utils import Utils
from drupdates.settings import Settings
from drupdates.settings import DrupdatesError
from drupdates.drush import Drush
from git import Repo

class DrupdatesBuildError(DrupdatesError):
    """ Parent Drupdates site build error. """

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
        self.standup_site()
        st_cmds = ['st']
        try:
            repo_status = Drush.call(st_cmds, self._site_name, True)
        except DrupdatesError as st_error:
            raise DrupdatesBuildError(20, st_error.msg)
        finally:
            web_root = self.settings.get('webrootDir')
            folder = os.path.join(self.site_dir, web_root)
            self.file_cleanup(folder)
        if not 'bootstrap' in repo_status:
            msg = "{0} failed to Stand-up properly after running drush qd".format(self._site_name)
            raise DrupdatesBuildError(20, msg)
        self.utilities.sys_commands(self, 'postBuildCmds')
        return "Site build for {0} successful".format(self._site_name)

    def standup_site(self):
        """ Using the drush core-quick-drupal (qd) command stand-up a Drupal site."""
        qd_cmds = self.settings.get('qdCmds')
        if self.settings.get('useMakeFile'):
            make_file = self.utilities.find_make_file(self._site_name, self.site_dir)
            qd_cmds += "--makefile={0}".format(make_file)
        try:
            Drush.call(qd_cmds, self._site_name)
        except DrupdatesError as standup_error:
            raise standup_error

    def file_cleanup(self, site_webroot):
        """ Drush sets the folder permissions for some file to be 0444, convert to 0777. """
        si_files = self.settings.get('drushSiFiles')
        for name in si_files:
            complete_name = os.path.join(site_webroot, name)
            if os.path.isfile(complete_name) or os.path.isdir(complete_name):
                try:
                    os.chmod(complete_name, 0777)
                except OSError:
                    msg = "Couldn't change file permission for {0}".format(complete_name)
                    raise DrupdatesBuildError(20, msg)
