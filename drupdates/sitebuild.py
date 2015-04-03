""" Drupdates Site building module. """
import git, os
from drupdates.utils import Utils
from drupdates.settings import Settings
from drupdates.drush import Drush
from drupdates.constructors.datastores import Datastores
from git import Repo

class Sitebuild(object):
    """ Build out the repository folder. """

    def __init__(self, siteName, ssh, working_dir):
        self.settings = Settings()
        self._site_name = siteName
        self.site_dir = os.path.join(working_dir, self._site_name)
        self.ssh = ssh
        self.drush = Drush()
        self.utilities = Utils()

    def build(self):
        """ Core build method. """
        working_branch = self.settings.get('workingBranch')
        if not Utils.remove_dir(self.site_dir):
            return False
        self.utilities.sys_commands(self, 'preBuildCmds')
        repository = Repo.init(self.site_dir)
        remote = git.Remote.create(repository, self._site_name, self.ssh)
        try:
            remote.fetch(working_branch)
        except git.exc.GitCommandError as error:
            msg = "{0}: Could not checkout {1}. \n".format(self._site_name, working_branch)
            msg += "Error: {2}".format(error)
            print msg
            return False
        git_repo = repository.git
        git_repo.checkout('FETCH_HEAD', b=working_branch)
        if self.settings.get('useMakeFile'):
            self.utilities.make_site(self._site_name, self.site_dir)
        st_cmds = ['st']
        repo_status = Drush.call(st_cmds, self._site_name, True)
        if not isinstance(repo_status, dict):
            print "{0} failed to respond to drush status".format(self._site_name)
            return False
        # If this is not a Drupal repo move to the next repo
        if not 'drupal-version' in repo_status:
            print "{0}, from drush pm-status: this isn't a drupal site".format(self._site_name)
            return False
        ret = True
        if not 'bootstrap' in repo_status:
            # Re-build database if it fails go to the next repo
            if 'site' in repo_status:
                site = os.path.basename(repo_status['site'])
            else:
                site = 'default'
            ret = self.construct_site(site)
        if ret and self.settings.get('importBackup'):
            # Import the backup file
            ret = self.import_backup()
        self.utilities.sys_commands(self, 'postBuildCmds')
        return ret
        
    def construct_site(self, site='default'):
        """ Rebulid the Drupal site: build DB, settings.php, etc..."""
        build_db = Datastores().build(self._site_name)
        if not build_db:
            print "Site database build failed for {0}".format(self._site_name)
            return False
        # Perform Drush site-install to get a base settings.php file
        si_cmds = ['si', 'minimal', '-y', '--sites-subdir=' + site]
        Drush.call(si_cmds, self._site_name)
        st_cmds = ['st']
        repo_status = Drush.call(st_cmds, self._site_name, True)
        if not 'bootstrap' in repo_status:
            print "Bootstrap failed after site install for {0}".format(self._site_name)
            return False
        drush_dd = Drush.call(['dd', '@drupdates.' + self._site_name])
        site_webroot = drush_dd[0]
        si_files = self.settings.get('drushSiFiles')
        for name in si_files:
            complete_name = os.path.join(site_webroot, name)
            if os.path.isfile(complete_name) or os.path.isdir(complete_name):
                os.chmod(complete_name, 0777)
        return True

    def import_backup(self):
        """ Import a site back-up

        Note: the back-up sife most follow the <siteName>.sql" naming convention"

        """
        import_db = self.drush.db_import(self._site_name)
        return import_db
