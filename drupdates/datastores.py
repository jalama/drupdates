from drupdates.utils import *
import abc

class datastores(Plugin):

  def __init__(self, siteName):
    # load the Plugin _plugins property
    Plugin.__init__(self)
    self.localsettings = Settings()
    self._tool = self.localsettings.get('datastoreDriver').lower()
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
    plugins = self._plugins
    self.__plugin = self.loadPlugin(plugins[value])

  @property
  def _site(self):
    return self.__site
  @_site.setter
  def _site(self, value):
    self.__site = value

  def build(self):
    class_ = getattr(self._plugin, self._tool)
    instance = class_()
    return instance.create(self._site)

  def dbSettings(self):
    class_ = getattr(self._plugin, self._tool)
    instance = class_()
    return instance.driverSettings()


class datastore(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def create(self, site): pass

  @abc.abstractmethod
  def driverSettings(self): pass

