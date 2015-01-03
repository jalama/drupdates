from drupdates.utils import *
import abc

class pmtools(Plugin):

  def __init__(self, siteName):
    Plugin.__init__(self)
    self.localsettings = Settings()
    self._tool = self.localsettings.get('pmName').lower()
    self._plugin = self._tool
    self._site = siteName
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
  def _site(self):
    return self.__site
  @_site.setter
  def _site(self, value):
    self.__site = value

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

  @property
  def _description(self):
      return self.__description
  @_description.setter
  def _description(self, value):
    descriptionList = []
    descriptionList.append("Git Hash = <" + value + ">")
    descriptionList.append("Post deployment steps:")
    descriptionList.append("drush @" + self._site +" updb -y")
    self.__description = '\n'.join(descriptionList)

  def deployTicket(self, env, commitHash):
    self._description = commitHash
    self._targetDate = self.localsettings.get('targetDate')
    return self._instance.submitDeployTicket(self._site, env, self._description, self._targetDate)

class pmTool(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def submitDeployTicket(self, site, environments, description, targetDate): pass
