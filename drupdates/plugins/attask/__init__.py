from drupdates.utils import *

# Work with AtTask
class attask(Plugin):

  @property
  def _attaskAPIURL(self):
    return self.__attaskAPIURL
  @_attaskAPIURL.setter
  def _attaskAPIURL(self, value):
    base = settings.get('attaskBaseURL')
    API = settings.get('attaskAPIVersion')
    self.__attaskAPIURL = base + 'api/' + API + '/'

  @property
  def _pmLabel(self):
    return self.__pmLabel
  @_pmLabel.setter
  def _pmLabel(self, value):
    self.__pmLabel = settings.get('pmName')

  @property
  def _sessionID(self):
    return self.__sessionID
  @_sessionID.setter
  def _sessionID(self, value):
    # Get a session ID from AtTask
    attaskPword = settings.get('attaskPword')
    attaskUser = settings.get('attaskUser')
    atParams = {'username': attaskUser, 'password': attaskPword}
    loginURL = self._attaskAPIURL + settings.get('attaskLoginUrl')
    response = apiCall(loginURL, self._pmLabel, 'post', params = atParams)
    if response == False:
      self.__sessionID = False
    else:
      self.__sessionID = responseDictionary['data']['sessionID']

  def submitDeployTicket(self, site, environments, description, targetDate):
    """ Submit a Deployment request to AtTask

    site -- The site the ticket is for
    environments -- The name(s) of the environments to deploy to
    description -- The description text to go in the task
    targetDate -- The date to put in the label fo the ticket

    """
    attaskProjectID = settings.get('webMaintProjectID')
    devOpsTeamID = settings.get('webOpsTeamID')
    attaskBaseURL = settings.get('attaskBaseURL')
    attaskAssigneeType = settings.get('attaskAssigneeType')
    sessparam = {}
    if self._sessionID
      sessparam['SessionID'] = self._sessionID
    else
      return False
    message = {}
    for environment in environments
      title = environment + ' Deployment for ' + site +' w.e. ' + targetDate
      atParams = {'name': title, 'projectID': webMaintProjectID, attaskAssigneeType: devOpsTeamID, 'description': description}
      response = apiCall(self._attaskAPIURL, self._pmLabel, 'post', params = atParams, headers = sessparam)
      if not response = False
        data = response['data']
        message[site][environment] = "The " + environment + " deploy ticket is {0}task/view/?ID={1}".format(attaskBaseURL, data['ID'])
      else
        message[site][environment] = "The " + environment + " deploy ticket did not submit to AtTask properly"
    return message
