""" Module handles the heavy lifting, building the various site directories. """
import git, shutil, os, yaml, tempfile, distutils.core
from drupdates.utils import Utils
from drupdates.settings import Settings
from drupdates.settings import DrupdatesError
from drupdates.drush import Drush
from drupdates.constructors.pmtools import Pmtools
from git import Repo

class DrupdatesUpdateError(DrupdatesError):
    """ Parent Drupdates site update error. """

class Siteupdate(object):
    """ Update the modules and/or core in a completely built Drupal site. """

    def __init__(self, site_name, ssh, working_dir):
        self.settings = Settings()
        self.working_branch = self.settings.get('workingBranch')
        self._site_name = site_name
        self.site_dir = os.path.join(working_dir, self._site_name)
        self.ssh = ssh
        self.utilities = Utils()
        self.site_web_root = None
        self._commit_hash = None
        self.repo_status = None
        self._module_dir = None

    @property
    def commit_hash(self):
        """ commit_hash getter. """
        return self._commit_hash

    @commit_hash.setter
    def commit_hash(self, value):
        """ commit_hash setter. """
        self._commit_hash = value

    def update(self):
        """ Set-up to and run Drush update(s) (i.e. up or ups). """
        report = {}
        self.utilities.sys_commands(self, 'preUpdateCmds')
        st_cmds = ['st']
        self.repo_status = Drush.call(st_cmds, self._site_name, True)
        if not isinstance(self.repo_status, dict):
            msg = "Repo {0} failed call to drush status during update".format(self._site_name)
            report['status'] = msg
            return report
        try:
            updates = self.run_updates()
        except DrupdatesError as updates_error:
            raise updates_error
        # If no updates move to the next repo
        if not updates:
            self.commit_hash = ""
            report['status'] = "Did not have any updates to apply"
            return report
        msg = '\n'.join(updates)
        # Call dr.call() without site alias argument, aliaes comes after dd argument
        drush_dd = Drush.call(['dd', '@drupdates.' + self._site_name])
        self.site_web_root = drush_dd[0]
        use_make_file = self.settings.get('useMakeFile')
        if self.settings.get('buildSource') == 'make' and use_make_file:
            shutil.rmtree(self.site_web_root)
        else:
            rebuilt = self.rebuild_web_root()
            if not rebuilt:
                report['status'] = "The webroot re-build failed."
                if use_make_file:
                    make_err = " Ensure the make file format is correct "
                    make_err += "and Drush make didn't fail on a bad patch."
                    report['status'] += make_err
                return report
        drush_path = os.path.join(self.site_web_root, 'drush')
        if os.path.isdir(drush_path):
            self.utilities.remove_dir(drush_path)

        self.git_changes(msg)
        report['status'] = "The following updates were applied \n {0}".format(msg)
        report['commit'] = "The commit hash is {0}".format(self.commit_hash)
        self.utilities.sys_commands(self, 'postUpdateCmds')
        if self.settings.get('submitDeployTicket') and self.commit_hash:
            report[self._site_name] = {}
            pm_name = self.settings.get('pmName').title()
            try:
                report[self._site_name][pm_name] = Pmtools().deploy_ticket(self._site_name,
                                                                           self.commit_hash)
            except DrupdatesError as api_error:
                report[self._site_name][pm_name] = api_error.msg
        return report

    def run_updates(self):
        """ Run the site updates.

        The updates are done either by downloading the updates, updating the make
        file or both.

        """
        updates = False
        if self.settings.get('useMakeFile'):
            ups_cmds = self.settings.get('upsCmds')
            updates_ret = {}
            try:
                updates_ret = Drush.call(ups_cmds, self._site_name, True)
            except DrupdatesError as updates_error:
                parse_error = updates_error.msg.split('\n')
                if parse_error[2].strip() == "Drush message:":
                    updates = []
                else:
                    raise updates_error
            else:
                updates = []
                for module, update in updates_ret.items():
                    api = update['api_version']
                    current = update['existing_version'].replace(api + '-', '')
                    candidate = update['candidate_version'].replace(api + '-', '')
                    self.update_make_file(module, current, candidate)
                    updates.append("Update {0} from {1} to {2}".format(module, current, candidate))
            if not self.settings.get('buildSource') == 'make':
                self.utilities.make_site(self._site_name, self.site_dir)
        else:
            up_cmds = self.settings.get('upCmds')
            try:
                updates_ret = Drush.call(up_cmds, self._site_name)
            except DrupdatesError as updates_error:
                raise updates_error
            else:
                updates = Siteupdate.read_update_report(updates_ret)
        return updates

    @staticmethod
    def read_update_report(lst):
        """ Read the report produced the the Drush pm-update command. """
        updates = []
        for line in lst:
            # build list of updates, when you hit a blank line you are done
            # note: if there are no updates the first line will be blank
            if line:
                updates.append(line)
            else:
                break
        if len(updates) <= 1:
            updates = False
        return updates

    def update_make_file(self, module, current, candidate):
        """ Update the make file.

        Keyword arguments:
        module -- the drupal module or core (required)
        current -- the current version
        candidate -- the version to update two

        """
        make_file = self.utilities.find_make_file(self._site_name, self.site_dir)
        make_format = self.settings.get('makeFormat')
        if make_format == 'make':
            openfile = open(make_file)
            makef = openfile.read()
            openfile.close()
            current_str = 'projects[{0}][version] = \"{1}\"'.format(module, current)
            candidate_str = 'projects[{0}][version] = \"{1}\"'.format(module, candidate)
            newdata = makef.replace(current_str, candidate_str)
            openfile = open(make_file, 'w')
            openfile.write(newdata)
            openfile.close()
        elif make_format == 'yaml':
            make = open(make_file)
            makef = yaml.load(make)
            make.close()
            makef['projects'][module]['version'] = str(candidate)
            openfile = open(make_file, 'w')
            yaml.dump(makef, openfile, default_flow_style=False)

    def git_changes(self, msg):
        """ add/remove changed files.

        notes:
        - Will ignore file mode changes and anything in the commonIgnore setting.
        - Will attempt to ignore any sqlite databases left behind

        """
        os.chdir(self.site_dir)
        repository = Repo(self.site_dir)
        git_repo = repository.git
        for ignore_file in self.settings.get('commonIgnore'):
            try:
                git_repo.checkout(os.path.join(self.site_web_root, ignore_file))
            except git.exc.GitCommandError:
                pass
        try:
            os.remove(os.path.join(self.site_web_root, 'drupdates.sqlite'))
        except OSError:
            pass
        if self.repo_status['modules'] and self.settings.get('ignoreCustomModules'):
            custom_module_dir = os.path.join(self.site_web_root,
                                             self.repo_status['modules'], 'custom')
            try:
                git_repo.checkout(custom_module_dir)
            except git.exc.GitCommandError:
                pass
        # Instruct Git to ignore file mode changes.
        cwriter = repository.config_writer('global')
        cwriter.set_value('core', 'fileMode', 'false')
        cwriter.release()
        # Add new/changed files to Git's index
        try:
            git_repo.add('./')
        except DrupdatesError as git_add_error:
            raise git_add_error
        # Remove deleted files from Git's index.
        deleted = git_repo.ls_files('--deleted')
        for filepath in deleted.split():
            git_repo.rm(filepath)
        # Commit all the changes.
        commit_author = self.settings.get('commitAuthor')
        git_repo.commit(m=msg, author=commit_author)
        # Save the commit hash for the Drupdates report to use.
        heads = repository.heads
        branch = heads[self.settings.get('workingBranch')]
        self.commit_hash = branch.commit
        # Push the changes to the origin repo.
        git_repo.push(self._site_name, self.working_branch)

    def rebuild_web_root(self):
        """ Rebuild the web root folder completely after running pm-update.
        Drush pm-update of Drupal Core deletes the .git folder therefore need to
        move the updated folder to a temp dir and re-build the webroot folder.
        """
        temp_dir = tempfile.mkdtemp(self._site_name)
        shutil.move(self.site_web_root, temp_dir)
        add_dir = self.settings.get('webrootDir')
        if add_dir:
            repository = Repo(self.site_dir)
            git_repo = repository.git
            git_repo.checkout(add_dir)
        else:
            repository = Repo.init(self.site_dir)
            try:
                remote = git.Remote.create(repository, self._site_name, self.ssh)
            except git.exc.GitCommandError as error:
                if not error.status == 128:
                    msg = "Could not establish a remote for the {0} repo".format(self._site_name)
                    print(msg)
            remote.fetch(self.working_branch)
            git_repo = repository.git
            try:
                git_repo.checkout('FETCH_HEAD', b=self.working_branch)
            except git.exc.GitCommandError as error:
                git_repo.checkout(self.working_branch)
            add_dir = self._site_name
        if 'modules' in self.repo_status:
            self._module_dir = self.repo_status['modules']
            shutil.rmtree(os.path.join(self.site_web_root, self._module_dir))
        if 'themes' in self.repo_status:
            theme_dir = self.repo_status['themes']
            shutil.rmtree(os.path.join(self.site_web_root, theme_dir))
        self.utilities.rm_common(self.site_web_root, temp_dir + '/' + add_dir)
        try:
            distutils.dir_util.copy_tree(temp_dir + '/' + add_dir,
                                         self.site_web_root,
                                         preserve_symlinks=1)
        except (OSError, distutils.errors.DistutilsFileError) as copy_error:
            raise DrupdatesUpdateError(20, copy_error)
        except IOError as error:
            msg = "Can't copy updates from: \n"
            msg += "{0} temp dir to {1}\n".format(temp_dir, self.site_web_root)
            msg += "Error: {2}".format(error.strerror)
            raise DrupdatesUpdateError(20, msg)
        shutil.rmtree(temp_dir)
        return True
