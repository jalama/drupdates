from drupdates.settings import Settings
from drupdates.utils import Plugin
import abc

class datastores(Plugin):

  def __init__(self):
    # load the Plugin _plugins property
    Plugin.__init__(self)
    self.settings = Settings()
    self._tool = self.settings.get('datastore').lower()
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
    self.__plugin = self.load_plugin(plugins[value])

  @property
  def _instance(self):
    return self.__instance
  @_instance.setter
  def _instance(self, value):
    class_ = getattr(self._plugin, self._tool)
    self.__instance = class_()

  def build(self, site):
    return self._instance.create(site)

  def createAlises(self):
    return self._instance.aliases()

  def cleanFiles(self):
    return self._instance.deleteFiles()

class datastore(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def create(self, site): pass

  @abc.abstractmethod
  def aliases(self): pass

  @abc.abstractmethod
  def deleteFiles(self): pass

