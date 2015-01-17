from drupdates.utils import *
import abc

class pmtools(Plugin):

  def __init__(self):
    Plugin.__init__(self)
    self.settings = Settings()
    self._tool = self.settings.get('pmName').lower()
    self._plugin = self._tool
    self._instance = ""

  @property
  def _tool(self):
    return self.__tool
  @_tool.setter
  def _tool(self, value):
    self.__tool = value

  @property
  def _plugin(self):
    return self.__plugin
  @_plugin.setter
  def _plugin(self, value):
    plugins = self._plugins
    self.__plugin = self.loadPlugin(plugins[value])

  @property
  def _instance(self):
    return self.__instance
  @_instance.setter
  def _instance(self, value):
    class_ = getattr(self._plugin, self._tool)
    self.__instance = class_()

  @property
  def _targetDate(self):
    return self.__targetDate
  @_targetDate.setter
  def _targetDate(self, value):
    # Get the date string for the following Friday
    if not value:
      today = datetime.date.today()
      # If today is a Friday, we skip to next Friday
      if datetime.datetime.today().weekday() == 4:
        friday = str(today + datetime.timedelta( (3-today.weekday())%7+1 ))
      else:
        friday = str(today + datetime.timedelta( (4-today.weekday()) % 7 ))
      self.__targetDate = friday
    else:
        self.__targetDate = value

  def description(self, site, gitHash):
    descriptionList = []
    descriptionList.append("Git Hash = <" + gitHash + ">")
    descriptionList.append("Post deployment steps:")
    descriptionList.append("drush @" + site +" updb -y")
    return '\n'.join(descriptionList)

  def deployTicket(self, site, commitHash):
<<<<<<< HEAD
    description = self.description(site, commitHash)
    print description
    environments = self.localsettings.get('deploymentTickets')
    self._targetDate = self.localsettings.get('targetDate')
=======
    description = self._description(site, commitHash)
    environments = self.settings.get('deploymentTickets')
    self._targetDate = self.settings.get('targetDate')
>>>>>>> cleanup - consistantly use settings in lieu of localsettings for attribute name
    return self._instance.submitDeployTicket(site, environments, description, self._targetDate)

class pmTool(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def submitDeployTicket(self, site, environments, description, targetDate): pass
