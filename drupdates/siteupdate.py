""" Module handles the heavy lifting, building the various site directories. """
import git, shutil, os, yaml, tempfile, datetime, time, copy
from drupdates.utils import Utils
from drupdates.settings import Settings
from drupdates.settings import DrupdatesError
from drupdates.drush import Drush
from drupdates.constructors.pmtools import Pmtools
from drupdates.sitebuild import Sitebuild
from git import Repo
from git import Actor

class DrupdatesUpdateError(DrupdatesError):
    """ Parent Drupdates site update error. """

class Siteupdate(object):
    """ Update the modules and/or core in a completely built Drupal site. """

    def __init__(self, site_name, ssh, working_dir):
        self.settings = Settings()
        self.working_branch = self.settings.get('workingBranch')
        self._site_name = site_name
        self.working_dir = working_dir
        self.site_dir = os.path.join(working_dir, self._site_name)
        self.ssh = ssh
        self.utilities = Utils()
        self.site_web_root = None
        self._commit_hash = None
        self.repo_status = None
        self.sub_sites = Drush.get_sub_site_aliases(self._site_name)

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
        self.repo_status = Drush.call(['st'], self._site_name, True)
        try:
            updates = self.run_updates()
        except DrupdatesError as updates_error:
            raise DrupdatesUpdateError(20, updates_error.msg)
        # If no updates move to the next repo
        if not updates:
            self.commit_hash = ""
            report['status'] = "Did not have any updates to apply"
            return report
        report['status'] = "The following updates were applied"
        report['updates'] = updates
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

        The updates are done either by downloading the updates, updating the
        make file or both.

        - First, run drush pm-updatestatus to get a list of eligible updates for
        the site/sub-sites.
        - Second, build the report to return to Updates().
        - Third, apply the updates.

        """
        updates = {}
        try:
            sites = self.get_sites_to_update()
        except DrupdatesError as update_status_error:
            raise DrupdatesUpdateError(20, update_status_error)
        if not sites['count']:
            return updates
        else:
            sites.pop('count')
        # Note: call Drush.call() without site alias as alias comes after dd argument.
        drush_dd = Drush.call(['dd', '@drupdates.' + self._site_name])
        self.site_web_root = drush_dd[0]
        # Create seperate commits for each project (ie module/theme)
        one_commit_per_project = self.settings.get('oneCommitPerProject')
        # Iterate through the site/sub-sites and perform updates, update files etc...
        sites_copy = copy.copy(sites)
        for site, data in sites.items():
            if 'modules' not in data:
                sites_copy.pop(site)
                continue
            modules = copy.copy(data['modules'])
            x = 0
            for project, descriptions in data['modules'].items():
                if self.settings.get('useMakeFile'):
                    self.update_make_file(project, descriptions['current'], descriptions['candidate'])
                if one_commit_per_project:
                    if x:
                        build = Sitebuild(self._site_name, self.ssh, self.working_dir)
                        build.build()
                    self._update_code(site, [project])
                    modules.pop(project)
                    updates = self._build_commit_message(sites_copy, site, project)
                    self._cleanup_and_commit(updates)
                x += 1
            if self.settings.get('buildSource') == 'make' and self.settings.get('useMakeFile'):
                self.utilities.make_site(self._site_name, self.site_dir)
            elif len(modules):
                self._update_code(site, modules.keys())
        if not one_commit_per_project:
            updates = self._build_commit_message(sites_copy)
            self._cleanup_and_commit(updates)
        return updates

    def get_sites_to_update(self):
        """ Build dictionary of sites/sub-sites and modules needing updated. """
        ups_cmds = self.settings.get('upsCmds')
        updates_ret = {}
        count = 0
        sites = {}
        sites[self._site_name] = {}
        for alias, data in self.sub_sites.items():
            sites[alias] = {}
        for site in sites:
            try:
                updates_ret = Drush.call(ups_cmds, site, True)
            except DrupdatesError as updates_error:
                parse_error = updates_error.msg.split('\n')
                if parse_error[2][0:14] == "Drush message:":
                    # If there are not updates to apply.
                    continue
                else:
                    raise updates_error
            else:
                # Parse the results of drush pm-updatestatus
                count += len(updates_ret)
                modules = {}
                for module, update in updates_ret.items():
                    modules[module] = {}
                    api = update['api_version']
                    modules[module]['current'] = update['existing_version'].replace(api + '-', '')
                    modules[module]['candidate'] = update['candidate_version'].replace(api + '-', '')
                    msg = "Update {0} from {1} to {2}"
                    modules[module]['report_txt'] = msg.format(module.title(),
                                                               modules[module]['current'],
                                                               modules[module]['candidate'])
                    sites[site]['modules'] = modules
        sites['count'] = count
        return sites

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

    def _update_code(self, site, modules):
        """ Run drush make or pm-update to make te actual code updates.

        Keyword arguments:
        site -- site alias of the site to update.
        modules -- list containing modules to update.

        """
        up_cmds = copy.copy(self.settings.get('upCmds'))
        up_cmds.append(" ".join(modules).encode())
        try:
            Drush.call(up_cmds, site)
        except DrupdatesError as updates_error:
            raise updates_error

    def _build_commit_message(self, sites, site = '', module = ''):
        """ Build a commit message for one project update or multiple.

        Keyword arguments:
        sites -- dictionary containing meta data about update for each site.
        site -- if only one site needs updated.
        module -- if only one module needs updated.

        """
        msg = {}
        if module and site:
            msg[site] = [sites[site]['modules'][module]['report_txt']]
        else:
            for site, data in sites.items():
                msg[site] = []
                for module, status in data['modules'].items():
                    msg[site].append(status['report_txt'])
        return msg

    def _cleanup_and_commit(self, updates):
        """ Clean-up webroot and commit changes.

        Keyword arguments:
        updates -- list of update message to put in commit message.

        """
        self._clean_up_web_root()
        self._git_apply_changes(updates)

    def _git_apply_changes(self, updates):
        """ add/remove changed files.

        Keyword arguments:
        updates -- list of update message to put in commit message.

        notes:
        - Will ignore file mode changes and anything in the commonIgnore setting.

        """
        os.chdir(self.site_dir)
        repo = Repo(self.site_dir)
        for ignore_file in self.settings.get('commonIgnore'):
            try:
                repo.git.checkout(os.path.join(self.site_web_root, ignore_file))
            except git.exc.GitCommandError:
                pass
        if self.repo_status['modules'] and self.settings.get('ignoreCustomModules'):
            custom_module_dir = os.path.join(self.site_web_root,
                                             self.repo_status['modules'], 'custom')
            try:
                repo.git.checkout(custom_module_dir)
            except git.exc.GitCommandError:
                pass
        # Instruct Git to ignore file mode changes.
        cwriter = repo.config_writer('global')
        cwriter.set_value('core', 'fileMode', 'false')
        cwriter.release()
        # Add new/changed files to Git's index
        try:
            repo.git.add('--all')
        except git.exc.GitCommandError as git_add_error:
            raise DrupdatesUpdateError(20, git_add_error)
        # Remove deleted files from Git's index.
        deleted = repo.git.ls_files('--deleted')
        for filepath in deleted.split():
            repo.git.rm(filepath)
        # Commit all the changes.
        if self.settings.get('useFeatureBranch'):
            if self.settings.get('featureBranchName'):
                branch_name = self.settings.get('featureBranchName')
            else:
                ts = time.time()
                stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                branch_name = "drupdates-{0}".format(stamp)
            repo.git.checkout(self.working_branch, b=branch_name)
        else:
            branch_name  = self.settings.get('workingBranch')
            repo.git.checkout(self.working_branch)
        msg = ''
        for site, update in updates.items():
            msg += "\n{0} \n {1}".format(site, '\n'.join(update))
        commit_author = Actor(self.settings.get('commitAuthorName'), self.settings.get('commitAuthorEmail'))
        repo.index.commit(message=msg, author=commit_author)
        # Save the commit hash for the Drupdates report to use.
        heads = repo.heads
        branch = heads[branch_name]
        self.commit_hash = branch.commit
        # Push the changes to the origin repo.
        repo.git.push(self._site_name, branch_name)

    def _clean_up_web_root(self):
        """ Clean-up artifacts from drush pm-update/core-quick-drupal. """
        use_make_file = self.settings.get('useMakeFile')
        if self.settings.get('buildSource') == 'make' and use_make_file:
            # Remove web root folder if repo only ships a make file.
            shutil.rmtree(self.site_web_root)
        else:
            rebuilt = self._rebuild_web_root()
            if not rebuilt:
                report['status'] = "The webroot re-build failed."
                if use_make_file:
                    make_err = " Ensure the make file format is correct "
                    make_err += "and Drush make didn't fail on a bad patch."
                    report['status'] += make_err
                return report
        # Remove <webroot>/drush folder
        drush_path = os.path.join(self.site_web_root, 'drush')
        if os.path.isdir(drush_path):
            self.utilities.remove_dir(drush_path)
        try:
            # Remove all SQLite files
            os.remove(self.repo_status['db-name'])
            for alias, data in self.sub_sites.items():
                db_file = data['databases']['default']['default']['database']
                if os.path.isfile(db_file):
                    os.remove(db_file)
        except OSError:
            pass

    def _rebuild_web_root(self):
        """ Rebuild the web root folder completely after running pm-update.

        Drush pm-update of Drupal Core deletes the .git folder therefore need to
        move the updated folder to a temp dir and re-build the webroot folder.
        """
        temp_dir = tempfile.mkdtemp(self._site_name)
        shutil.move(self.site_web_root, temp_dir)
        add_dir = self.settings.get('webrootDir')
        if add_dir:
            repo = Repo(self.site_dir)
            repo.git.checkout(add_dir)
        else:
            repo = Repo.init(self.site_dir)
            try:
                remote = git.Remote.create(repo, self._site_name, self.ssh)
            except git.exc.GitCommandError as error:
                if not error.status == 128:
                    msg = "Could not establish a remote for the {0} repo".format(self._site_name)
                    print(msg)
            remote.fetch(self.working_branch)
            try:
                repo.git.checkout('FETCH_HEAD', b=self.working_branch)
            except git.exc.GitCommandError as error:
                repo.git.checkout(self.working_branch)
            add_dir = self._site_name
        if 'modules' in self.repo_status:
            module_dir = self.repo_status['modules']
            shutil.rmtree(os.path.join(self.site_web_root, module_dir))
        if 'themes' in self.repo_status:
            theme_dir = self.repo_status['themes']
            shutil.rmtree(os.path.join(self.site_web_root, theme_dir))
        self.utilities.rm_common(self.site_web_root, os.path.join(temp_dir, add_dir))
        try:
            Utils.copytree(os.path.join(temp_dir, add_dir),
                                         self.site_web_root,
                                         symlinks=True)
        except OSError as copy_error:
            raise DrupdatesUpdateError(20, copy_error)
        except IOError as error:
            msg = "Can't copy updates from: \n"
            msg += "{0} temp dir to {1}\n".format(temp_dir, self.site_web_root)
            msg += "Error: {0}".format(error.strerror)
            raise DrupdatesUpdateError(20, msg)
        shutil.rmtree(temp_dir)
        return True
