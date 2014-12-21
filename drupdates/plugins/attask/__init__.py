from drupdates.utils import *

# Work with AtTask
class attask:

  def __init__(self):
    # Get a session ID from AtTask
    pmUser = settings.get('pmUser')
    pmPword = settings.get('pmPword')
    pmURL = settings.get('pmURL')
    pmLabel = settings.get('pmLabel')

    atParams = {'username': pmUser, 'password': pmPword}
    response = apiCall(pmURL, pmLabel, 'post', params = atParams)
    if response == False:
      return response
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
    pmURL = settings.get('pmURL')
    pmLabel = settings.get('pmLabel')
    baseURL = settings.get('basePmURL')
    sessparam = {'SessionID': self.__sessionID}
    title = env + ' Deployment for ' + siteName +' w.e. ' + targetDate
    atParams = {'name': title, 'projectID': webMaintProjectID, 'teamID': webOpsTeamID, 'description': description}
    response = apiCall(pmURL, pmLabel, 'post', params = atParams, headers = sessparam)
    data = response['data']
    message = "The Staging deploy ticket is {0}task/view/?ID={1}".format(baseUrl, data['ID'])
    return message
