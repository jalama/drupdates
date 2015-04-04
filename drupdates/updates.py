""" Primary Drupdates Module. """
import os
from drupdates.settings import Settings
from drupdates.constructors.repos import Repos
from drupdates.constructors.pmtools import Pmtools
from drupdates.constructors.reports import Reports
from drupdates.constructors.datastores import Datastores
from drupdates.sitebuild import Sitebuild
from drupdates.siteupdate import Siteupdate


class Updates(object):
    """ Run through the working directories and sites updating them. """

    def __init__(self):
        self.settings = Settings()
        self.working_dirs = self.settings.get('workingDir')
        self.single_site = ''
        if isinstance(self.working_dirs, str):
            self.working_dirs = [self.working_dirs]
            self.single_site = self.settings.get('singleSite')

    def run_updates(self):
        """ Drupdates main function. """
        report = {}
        for current_working_dir in self.working_dirs:
            current_working_dir = Updates.check_working_dir(current_working_dir)
            if not current_working_dir:
                continue
            self.working_dir_settings(current_working_dir)
            update = self.update_site(current_working_dir)
            report[current_working_dir] = update
        reporting = Reports()
        reporting.send(report)

    def update_site(self, working_dir):
        """ Run updates for an individual working directory. """
        report = {}
        datastore = Datastores()
        datastore.create_alises(working_dir)
        blacklist = self.settings.get('blacklist')
        sites = Repos().get()
        if self.single_site:
            sites = {self.single_site : sites[self.single_site]}
        for site_name, ssh in sites.iteritems():
            report[site_name] = {}
            if site_name in blacklist:
                continue

            if self.settings.get('buildRepos'):
                builder = Sitebuild(site_name, ssh, working_dir)
                build = builder.build()
                if not build:
                    continue

            if self.settings.get('runUpdates'):
                updater = Siteupdate(site_name, ssh, working_dir)
                update = updater.update()
                report[site_name] = update
                if self.settings.get('submitDeployTicket') and updater.commit_hash:
                    deploys = Pmtools().deploy_ticket(site_name, updater.commit_hash)
                    pm_name = self.settings.get('pmName').title()
                    report[site_name][pm_name] = deploys
        self.settings.reset()
        datastore.clean_files()
        return report

    @staticmethod
    def check_working_dir(directory):
        """ Ensure the directory is writable. """
        parts = directory.split('/')
        if parts[0] == '~' or parts[0].upper() == '$HOME':
            del parts[0]
            directory = os.path.join(os.path.expanduser('~'), '/'.join(parts))
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError as error:
                msg = 'Unable to create non-existant directory {0} \n'.format(directory)
                msg += 'Error: {0}\n'.format(error.strerror)
                msg += 'Moving to next working directory, if applicable'
                print msg
                return False
        filepath = os.path.join(directory, "text.txt")
        try:
            open(filepath, "w")
        except IOError:
            msg = 'Unable to write to directory {0} \n'.format(directory)
            msg += 'Moving to next working directory, if applicable'
            print msg
            return False
        os.remove(filepath)
        return directory

    def working_dir_settings(self, working_dir):
        """ Add custom settings for the working direcotry. """
        working_settings = os.path.join(working_dir, '.drupdates/settings.yaml')
        if os.path.isfile(working_settings):
            self.settings.add(working_settings, True)
