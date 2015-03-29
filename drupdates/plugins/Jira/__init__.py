""" Plugin to wotk with JIRA. """
from drupdates.utils import Utils
from drupdates.settings import Settings
from drupdates.constructors.pmtools import Pmtool
import json, os
from urlparse import urljoin

class Jira(Pmtool):
    """ Plugin to wotk with JIRA. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file = current_dir + '/settings/default.yaml'
        self.settings = Settings()
        self.settings.add(settings_file)
        base = self.settings.get('jiraBaseURL')
        api = self.settings.get('jiraAPIVersion')
        if not api.endswith('/'):
            api += '/'
        jira_api_base = urljoin(base, 'rest/api/')
        self._jira_api_url = urljoin(jira_api_base, api)

    def submit_deploy_ticket(self, site, environments, description, target_date):
        """ Submit a deployment ticket to JIRA/Agile Ready. """
        issue_uri = self.settings.get('jiraIssueURL')
        issue_url = urljoin(self._jira_api_url, issue_uri)
        jira_user = self.settings.get('jiraUser')
        jira_pword = self.settings.get('jiraPword')
        message = {}
        for environment in environments:
            request = self.build_reqest(site, environment, description, target_date)
            headers = {'content-type': 'application/json'}
            response = Utils.api_call(issue_url, 'Jira', 'post', data=request,
                                      auth=(jira_user, jira_pword), headers=headers)
            if not response == False:
                url = response['key']
                message[environment] = "The {0} deploy ticket is {1}".format(environment, url)
            else:
                message[environment] = "JIRA ticket submission failed for {0}".format(environment)
        return message

    def build_reqest(self, site, environment, description, target_date):
        """ Build the JSON request to be submitted to JIRA. """
        summary = '{0} Deployment for {1} w.e. {2}'.format(environment, site, target_date)
        request = {}
        request['fields'] = {}
        request['fields']['project'] = {'key' : self.settings.get('jiraProjectID')}
        request['fields']['summary'] = summary
        request['fields']['description'] = description
        request['fields']['issuetype'] = {'name': self.settings.get('jiraIssueType')}
        return json.dumps(request)

