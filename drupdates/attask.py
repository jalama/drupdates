from drupdates.utils import *
from drupdates.settings import *

#Work with AtTask

settings = Settings()

def getAtTaskSession():
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
    sessionID = responseDictionary['data']['sessionID']
    return sessionID


def submitAtTaskDeploy(site, env, description, targetDate, sessionID):
  """ Submit a Deployment request to AtTask

  env -- the Name of the environment to deploy to
  description -- the description test to go in the task
  targetDate -- the date to put in the lable fo the ticket
  sessionID -- The session ID form AtTask that authenticates this submission

  """
  webMaintProjectID = settings.get('webMaintProjectID')
  webOpsTeamID = settings.get('webOpsTeamID')
  pmURL = settings.get('pmURL')
  pmLabel = settings.get('pmLabel')

  sessparam = {'SessionID': sessionID}
  title = env + ' Deployment for ' + siteName +' w.e. ' + targetDate
  atParams = {'name': title, 'projectID': webMaintProjectID, 'teamID': webOpsTeamID, 'description': description}
  response = apiCall(pmURL, pmLabel, 'post', params = atParams, headers = sessparam)
  # r = requests.post('baseAtTaskUrl+taskAtTaskURL', params = params2, headers = sessparam)
  return response
