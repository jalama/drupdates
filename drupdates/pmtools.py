from drupdates.utils import *

class pmtools:

  def __init__(self):
    plugins = getPlugins()
    self.__repoTool = settings.get('pmLabel').lower()
    self.__plugin = loadPlugin(plugins[self.__repoTool])

  def deploy(self):
    class_ = getattr(self.__plugin, self.__repoTool)
    instance = class_()
    return instance.submitDeployTicket()
