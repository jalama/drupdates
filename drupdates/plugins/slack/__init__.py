from drupdates.utils import *
from drupdates.constructors.reports import *
import json

class slack(Reports):

  def __init__(self):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)

  def sendMessage(self, reportText):
    """ Post the report to a Slack channel or DM a specific user."""
    url = self.settings.get('slackURL')
    user = self.settings.get('slackUser')
    payload = {}
    payload['text'] = reportText
    payload['new-bot-name'] = user
    dm = self.settings.get('slackRecipient')
    channel = self.settings.get('slackChannel')
    if dm:
        payload['channel'] = '@' + dm
    elif channel:
        payload['channel'] = '#' + dm
    response = utils.apiCall(url, 'Slack', 'post', data = json.dumps(payload))


