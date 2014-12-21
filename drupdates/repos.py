from drupdates.utils import *

class repos:

  def __init__(self):
    plugins = getPlugins()
    self.__repoTool = settings.get('gitRepoName').lower()
    self.__plugin = loadPlugin(plugins[self.__repoTool])

  def get(self):
    class_ = getattr(self.__plugin, self.__repoTool)
    instance = class_()
    return instance.gitRepos()



