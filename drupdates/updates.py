""" Primary Drupdates Module. """
from drupdates.settings import Settings
from drupdates.constructors.repos import repos
from drupdates.constructors.pmtools import pmtools
from drupdates.constructors.reports import reports
from drupdates.constructors.datastores import datastores
from drupdates.sitebuild import Sitebuild
from drupdates.siteupdate import Siteupdate

def main():
    """ Drupdates main function. """
    settings = Settings()
    report = {}
    sites = repos().get()
    pm_tool = pmtools()
    blacklist = settings.get('blacklist')
    single_site = settings.get('singleSite')
    datastore = datastores()
    datastore.createAlises()
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

    datastore.cleanFiles()
    reporting = reports()
    reporting.send(report)
