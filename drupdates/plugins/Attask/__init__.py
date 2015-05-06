""" Plugin to wotk with AtTask. """
from drupdates.settings import Settings
from drupdates.utils import Utils
from drupdates.constructors.pmtools import Pmtool
import os
from urlparse import urljoin

class Attask(Pmtool):
    """ Plugin to wotk with AtTask. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file = current_dir + '/settings/default.yaml'
        self.settings = Settings()
        self.settings.add(settings_file)
        self._pm_label = self.settings.get('pmName')
        base = self.settings.get('attaskBaseURL')
        api = self.settings.get('attaskAPIVersion')
        api_base = urljoin(base, 'attask/api/')
        self._attask_api_url = urljoin(api_base, api)

    def get_session_id(self):
        """ Get a session ID from AtTask. """
        attask_pword = self.settings.get('attaskPword')
        attask_user = self.settings.get('attaskUser')
        at_params = {'username': attask_user, 'password': attask_pword}
        login_url = urljoin(self._attask_api_url, self.settings.get('attaskLoginUrl'))
        response = Utils.api_call(login_url, self._pm_label, 'post', params=at_params)
        if response == False:
            return False
        else:
            return response['data']['sessionID']

    def submit_deploy_ticket(self, site, environments, description, target_date):
        """ Submit a Deployment request to AtTask.

        site -- The site the ticket is for
        environments -- The name(s) of the environments to deploy to
        description -- The description text to go in the task
        targetDate -- The date to put in the label fo the ticket

        """
        sessparam = {}
        session_id = self.get_session_id()
        # Make sure you can get a Session ID
        if session_id:
            sessparam['sessionID'] = session_id
        else:
            return False
        # Set-up AtTask request
        attask_project_id = self.settings.get('attaskProjectID')
        dev_ops_team_id = self.settings.get('devOpsTeamID')
        attask_base_url = self.settings.get('attaskBaseURL')
        attask_assignee_type = self.settings.get('attaskAssigneeType')
        task_url = urljoin(self._attask_api_url, self.settings.get('attaskTaskURL'))
        message = {}
        for environment in environments:
            title = environment + ' Deployment for ' + site +' w.e. ' + target_date
            at_params = {'name': title, 'projectID': attask_project_id,
                         attask_assignee_type: dev_ops_team_id, 'description': description}
            response = Utils.api_call(task_url, self._pm_label, 'post',
                                      params=at_params, headers=sessparam)
            if not response == False:
                data = response['data']
                msg = "The {0} deploy ticket is".format(environment)
                msg += " <{0}task/view?ID={1}>".format(attask_base_url, data['ID'])
                message[environment] = msg
            else:
                msg = "The {0} deploy ticket did not submit to".format(environment)
                msg += "{0} properly".format(self._pm_label)
                message[environment] = msg
        return message
