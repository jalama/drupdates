""" Parent class for plugins work with Project Management Tools. """
from drupdates.settings import Settings
from drupdates.plugins import Plugin
import abc, datetime

class Pmtools(Plugin):
    """ Submit requests to Project Management tools. """

    def __init__(self):
        self.settings = Settings()
        tool = self.settings.get('pmName').title()
        self._plugin = Plugin.load_plugin(tool)
        class_ = getattr(self._plugin, tool)
        self._instance = class_()

    def target_date(self):
        """ Get the date string for the following Friday. """
        value = self.settings.get('targetDate')
        if not value:
            today = datetime.date.today()
            # If today is a Friday, we skip to next Friday
            if datetime.datetime.today().weekday() == 4:
                friday = str(today + datetime.timedelta((3-today.weekday()) % 7 + 1))
            else:
                friday = str(today + datetime.timedelta((4-today.weekday()) % 7))
            return friday
        else:
            return value

    @staticmethod
    def description(site, git_hash):
        """ Collect data for ticket's descriotion field. """
        description_list = []
        description_list.append("Git Hash = <" + git_hash + ">")
        description_list.append("Post deployment steps:")
        description_list.append("drush @" + site +" updb -y")
        return '\n'.join(description_list)

    def deploy_ticket(self, site, commit_hash):
        """ Submit ticket requesting deployment(s). """
        description = Pmtools.description(site, commit_hash)
        environments = self.settings.get('deploymentTickets')
        target = self.target_date()
        return self._instance.submit_deploy_ticket(site, environments, description, target)

class Pmtool(object):
    """ Abstract class to work with Project Management tool. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def submit_deploy_ticket(self, site, environments, description, target_date):
        """ Abstract method ticket requesting deployment(s). """
        pass
