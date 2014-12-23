from drupdates.utils import *

# Work with AtTask
class attask(Plugin):

  @property
  def _sessionID(self):
      return self.__sessionID
  @_sessionID.setter
  def _sessionID(self, value):
    # Get a session ID from AtTask
    attaskPword = settings.get('attaskPword')
    attaskPword = settings.get('attaskPword')
    attaskAPIURL = settings.get('attaskAPIURL')
    pmLabel = settings.get('pmLabel')

    atParams = {'username': attaskUser, 'password': attaskPword}
    response = apiCall(attaskAPIURL, pmLabel, 'post', params = atParams)
    if response == False:
      self.__sessionID = False
    else:
      self.__sessionID = responseDictionary['data']['sessionID']

  def submitDeployTicket(self, site, env, description, targetDate):
    """ Submit a Deployment request to AtTask

    env -- the Name of the environment to deploy to
    description -- the description test to go in the task
    targetDate -- the date to put in the lable fo the ticket

    """
    webMaintProjectID = settings.get('webMaintProjectID')
    webOpsTeamID = settings.get('webOpsTeamID')
    attaskAPIURL = settings.get('attaskAPIURL')
    pmLabel = settings.get('pmLabel')
    attaskBaseURL = settings.get('attaskBaseURL')
    sessparam = {}
    if self._sessionID
      sessparam['SessionID'] =self._sessionID}
    else
      return False
    title = env + ' Deployment for ' + siteName +' w.e. ' + targetDate
    atParams = {'name': title, 'projectID': webMaintProjectID, 'teamID': webOpsTeamID, 'description': description}
    response = apiCall(attaskAPIURL, pmLabel, 'post', params = atParams, headers = sessparam)
    data = response['data']
    message = "The Staging deploy ticket is {0}task/view/?ID={1}".format(attaskBaseURL, data['ID'])
    return message
