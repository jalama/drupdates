""" Primary Drupdates Module. """
from drupdates.settings import Settings
from drupdates.constructors.repos import Repos
from drupdates.constructors.pmtools import pmtools
from drupdates.constructors.reports import Reports
from drupdates.constructors.datastores import Datastores
from drupdates.sitebuild import Sitebuild
from drupdates.siteupdate import Siteupdate

def main():
    """ Drupdates main function. """
    settings = Settings()
    report = {}
    sites = Repos().get()
    pm_tool = pmtools()
    blacklist = settings.get('blacklist')
    single_site = settings.get('singleSite')
    datastore = Datastores()
    datastore.create_alises()
    if single_site:
        sites = {single_site : sites[single_site]}
    for site_name, ssh in sites.iteritems():
        report[site_name] = {}
        if site_name in blacklist:
            continue

        if settings.get('buildRepos'):
            builder = Sitebuild(site_name, ssh)
            build = builder.build()
            if not build:
                continue

        if settings.get('runUpdates'):
            updater = Siteupdate(site_name, ssh)
            update = updater.update()
            report[site_name] = update
            if settings.get('submitDeployTicket') and updater.commit_hash:
                deploys = pm_tool.deployTicket(site_name, updater.commit_hash)
                report[site_name]['pmtool'] = deploys

    datastore.clean_files()
    reporting = Reports()
    reporting.send(report)
