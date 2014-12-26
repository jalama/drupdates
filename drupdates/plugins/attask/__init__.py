from drupdates.utils import *
from drupdates.pmtools import *

# Work with AtTask
class attask(pmTool, Settings):

  def __init__(self):
    currentDir = os.path.dirname(os.path.realpath(__file__))
    self.localsettings = Settings(currentDir)
    API = self.localsettings.get('attaskAPIVersion')
    self._attaskAPIURL = API
    self._pmLabel = self.localsettings.get('pmName')
    self._sessionID = ""

  @property
  def _attaskAPIURL(self):
    return self.__attaskAPIURL
  @_attaskAPIURL.setter
  def _attaskAPIURL(self, value):
    base = self.localsettings.get('attaskBaseURL')
    self.__attaskAPIURL = base + 'attask/api/' + value + '/'

  @property
  def _pmLabel(self):
    return self.__pmLabel
  @_pmLabel.setter
  def _pmLabel(self, value):
    self.__pmLabel = value

  @property
  def _sessionID(self):
    return self.__sessionID
  @_sessionID.setter
  def _sessionID(self, value):
    # Get a session ID from AtTask
    attaskPword = self.localsettings.get('attaskPword')
    attaskUser = self.localsettings.get('attaskUser')
    atParams = {'username': attaskUser, 'password': attaskPword}
    loginURL = self._attaskAPIURL + self.localsettings.get('attaskLoginUrl')
    response = apiCall(loginURL, self._pmLabel, 'post', params = atParams)
    if response == False:
      self.__sessionID = False
    else:
      self.__sessionID = response['data']['sessionID']

  def submitDeployTicket(self, site, environments, description, targetDate):
    """ Submit a Deployment request to AtTask

    site -- The site the ticket is for
    environments -- The name(s) of the environments to deploy to
    description -- The description text to go in the task
    targetDate -- The date to put in the label fo the ticket

    """
    sessparam = {}
    # Make sure you can get a Session ID
    if self._sessionID:
      sessparam['SessionID'] = self._sessionID
    else:
      return False
    # Set-up AtTask request
    attaskProjectID = self.localsettings.get('attaskProjectID')
    devOpsTeamID = self.localsettings.get('devOpsTeamID')
    attaskBaseURL = self.localsettings.get('attaskBaseURL')
    attaskAssigneeType = self.localsettings.get('attaskAssigneeType')
    taskURL = self._attaskAPIURL + self.localsettings.get('attaskTaskURL')
    message = {}
    message[site] = {}
    for environment in environments:
      title = environment + ' Deployment for ' + site +' w.e. ' + targetDate
      atParams = {'name': title, 'projectID': attaskProjectID, attaskAssigneeType: devOpsTeamID, 'description': description}
      response = apiCall(taskURL, self._pmLabel, 'post', params = atParams, headers = sessparam)
      if not response == False:
        data = response['data']
        message[site][environment] = "The " + environment + " deploy ticket is {0}task/view?ID={1}".format(attaskBaseURL, data['ID'])
      else:
        message[site][environment] = "The " + environment + " deploy ticket did not submit to AtTask properly"
    return message
