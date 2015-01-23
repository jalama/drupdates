from drupdates.utils import *
from drupdates.constructors.pmtools import *
import json

class jira(pmTool):

  def __init__(self):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)

  @property
  def _jiraAPIURL(self):
    return self.__jiraAPIURL
  @_jiraAPIURL.setter
  def _jiraAPIURL(self, value):
    base = self.settings.get('jiraBaseURL')
    self.__jiraAPIURL = base + 'rest/api/' + value + '/'

  def submitDeployTicket(self, site, environments, description, targetDate):
    """Submit a deployment ticket to JIRA/Agile Ready"""
    API = self.settings.get('jiraAPIVersion')
    self._jiraAPIURL = API
    issueURL = self._jiraAPIURL + self.settings.get('jiraIssueURL')
    jiraUser = self.settings.get('jiraUser')
    jiraPword = self.settings.get('jiraPword')
    message = {}
    for environment in environments:
      request = self.buildReqest(site, environment, description, targetDate)
      headers = {'content-type': 'application/json'}
      r = utils.apiCall(issueURL, 'Jira', 'post', data = request, auth=(jiraUser, jiraPword), headers=headers)
      print r
      if not r == False:
        message[environment] = "The {0} deploy ticket is {1}".format(environment, r['key'])
      else:
        message[environment] = "The {0} deploy ticket did not submit to JIRA properly".format(environment)
    return message

  def buildReqest(self, site, environment, description, targetDate):
    request = {}
    request['fields'] = {}
    request['fields']['project'] = {'key' : self.settings.get('jiraProjectID')}
    request['fields']['summary'] ='{0} Deployment for {1} w.e. {2}'.format(environment, site, targetDate)
    request['fields']['description'] = description
    request['fields']['issuetype'] = {'name': self.settings.get('jiraIssueType')}
    return json.dumps(request)

