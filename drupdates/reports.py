from drupdates.utils import *
import abc, tempfile, shutil

class reports(Plugin):

  def __init__(self):
    # load the Plugin _plugins property
    Plugin.__init__(self)
    self.localsettings = Settings()
    self._tool = self.localsettings.get('reportingTool').lower()
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

  def send(self, report):
    reportText = ""
    for x in report:
      reportText += "{0} \n".format(x)
      for y in report[x]:
        reportText += "  {0} : {1} \n".format(y,report[x][y])
    return self._instance.sendMessage(reportText)

class datastore(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def sendMessage(self): pass
