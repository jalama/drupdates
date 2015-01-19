from drupdates.utils import *
from drupdates.constructors.repos import *
from drupdates.constructors.pmtools import *
from drupdates.constructors.reports import *
from drupdates.sitebuild import *
from drupdates.siteupdate import *

def main():
  settings = Settings()
  report = {}
  sites = repos().get()
  pmTool = pmtools()
  utilities = utils()
  blacklist = settings.get('blacklist')
  singleSite = settings.get('singleSite')
  if singleSite:
    sites = {singleSite : sites[singleSite]}
  for siteName, ssh in sites.iteritems():
    report[siteName] = {}
    if siteName in blacklist:
      continue

    if settings.get('buildRepos'):
      builder = sitebuild(siteName, ssh)
      build = builder.build()
      if not build:
        continue

    if settings.get('runUpdates'):
      updater = siteupdate(siteName, ssh)
      update = updater.update()
      report[siteName] = update
      if settings.get('submitDeployTicket') and updater.commitHash:
        deploys = pmTool.deployTicket(siteName, updater.commitHash)
        report[siteName]['pmtool'] = deploys

  utilities.deleteFiles()
  reporting = reports()
  reporting.send(report)
