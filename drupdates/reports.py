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

  def formatReport(self, report, text = ""):
    for x in report:
      if isinstance(report[x], dict):
        text += "{0} \n".format(x)
        text = self.formatReport(report[x], text)
      else:
        text += "\t{0} : {1} \n".format(x, report[x])
    return text

  def send(self, report):
    reportText = self.formatReport(report)
    return self._instance.sendMessage(reportText)

class datastore(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def sendMessage(self): pass
