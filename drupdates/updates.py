from drupdates.utils import *
from drupdates.constructors.repos import *
from drupdates.constructors.pmtools import *
from drupdates.constructors.reports import *
from drupdates.sitebuild import *
from drupdates.siteupdate import *

def main(self):
  self.settings = Settings()
  report = {}
  sites = repos().get()
  pmTool = pmtools()
  utilities = utils()
  blacklist = self.settings.get('blacklist')
  singleSite = self.settings.get('singleSite')
  if singleSite:
    sites = {singleSite : sites[singleSite]}
  for siteName, ssh in sites.iteritems():
    report[siteName] = {}
    if siteName in blacklist:
      continue

    if self.settings.get('buildRepos'):
      builder = sitebuild(siteName, ssh)
      build = builder.build()
      if not build:
        continue

    if self.settings.get('runUpdates'):
      updater = siteupdate(siteName, ssh)
      update = updater.update()
      report[siteName] = update
      if self.settings.get('submitDeployTicket') and updater.commitHash:
        deploys = pmTool.deployTicket(siteName, updater.commitHash)
        report[siteName]['pmtool'] = deploys

  utilities.deleteFiles()
  reporting = reports()
  reporting.send(report)
