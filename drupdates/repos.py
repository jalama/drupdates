from drupdates.utils import *
import abc

class repos(Plugin):

  def __init__(self):
    # load the Plugin _plugins property
    Plugin.__init__(self)
    self.localsettings = Settings()
    self._tool = self.localsettings.get('gitRepoName').lower()
    self._plugin = self._tool

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

  def get(self):
    class_ = getattr(self._plugin, self._tool)
    instance = class_()
    return instance.gitRepos()

class repoTool(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def gitRepos(self):
    """retrieve a list of repos"""
    return



