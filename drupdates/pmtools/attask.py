# This should get replaced by a generic plugin for PM VCS systems
def getAtTaskSession():
  # Get a session ID from AtTask
  atParams = {'username': pmUser, 'password': pmPword}
  response = apiCall(pmURL, pmLabel, 'post', params = atParams)
  if response == False:
    return response
  else:
    sessionID = responseDictionary['data']['sessionID']
    return sessionID


def submitAtTaskDeploy(env, description, targetDate, sessionID):
  """ Submit a Deployment request to AtTask

  env -- the Name of the environment to deploy to
  description -- the description test to go in the task
  targetDate -- the date to put in the lable fo the ticket
  sessionID -- The session ID form AtTask that authenticates this submission

  """
  sessparam = {'SessionID': sessionID}
  title = env + ' Deployment for ' + siteName +' w.e. ' + targetDate
  atParams = {'name': title, 'projectID': webMaintProjectID, 'teamID': webOpsTeamID, 'description': description}
  response = apiCall(pmURL, pmLabel, 'post', params = atParams, headers = sessparam)
  # r = requests.post('baseAtTaskUrl+taskAtTaskURL', params = params2, headers = sessparam)
  return response
