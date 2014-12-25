from drupdates.utils import *

class pmtools(Plugin):

  def __init__(self, siteName):
    self._tool = settings.get('pmName').lower()
    self._plugin = self._tool
    self._site = siteName

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
    self.__plugin = loadPlugin(self._plugins[value])

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
    # Get the data string for the following Friday
    targetDate = settings.get('targetDate')
    if not targetDate:
      today = datetime.date.today()
      # Today is a Friday, we skip to next Friday
      if datetime.datetime.today().weekday() == 4:
        friday = str(today + datetime.timedelta( (3-today.weekday())%7+1 ))
      else:
        friday = str(today + datetime.timedelta( (4-today.weekday()) % 7 ))
      self.__targetDate = friday

  def descriptionText(self, commitHash):
    descriptionList = []
    descriptionList.append("Git Hash = <" + commitHash + "> \n")
    descriptionList.append("Post deployment steps: \n")
    descriptionList.append("drush @" + self._site +" updb -y \n")
    description = '\n'.join(descriptionList)
    self.__description = description

  def deployTicket(self, env, commitHash):
    # Load the Plugin
    description = descriptionText(commitHash)
    class_ = getattr(self._plugin, self._tool)
    instance = class_()
    return instance.submitDeployTicket(self._site, env, description, self._targetDate)
