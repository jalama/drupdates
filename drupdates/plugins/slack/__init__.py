""" Send report using Slack. """
from drupdates.settings import Settings
from drupdates.utils import utils
from drupdates.constructors.reports import Report
import json, os

class Slack(Report):
    """ Slack report plugin. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.settings = Settings(current_dir)

    def send_message(self, report_text):
        """ Post the report to a Slack channel or DM a specific user."""
        url = self.settings.get('slackURL')
        user = self.settings.get('slackUser')
        payload = {}
        payload['text'] = report_text
        payload['new-bot-name'] = user
        direct = self.settings.get('slackRecipient')
        channel = self.settings.get('slackChannel')
        if direct:
            payload['channel'] = '@' + direct
        elif channel:
            payload['channel'] = '#' + direct
        utils.apiCall(url, 'Slack', 'post', data=json.dumps(payload))


