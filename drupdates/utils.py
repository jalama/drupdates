import datetime, requests, os, imp, yaml, urlparse
from os.path import expanduser

class utils(object):

  @staticmethod
  def apiCall (uri, name, method = 'get', **kwargs):
    """ Perform and API call, expecting a JSON response.  Largely a wrapper
    around the request module

    Keyword arguments:
    uri -- the uri of the Restful Web Service (required)
    name -- the human readable label for the service being called (required)
    method -- HTTP method to use (defaul = 'get')
    kwargs -- dictionary of arguments passed directly to requests module method

    """
    # Ensure uri is valid
    if not bool(urlparse.urlparse(uri).netloc):
      print("Error: {0} is not a valid url").format(uri)
      return False
    # FIXME: need to HTML escape passwords
    func = getattr(requests, method)
    args = {}
    for key, value in kwargs.iteritems():
      args[key] = value
    # if not user == '' and not pword == '':
    #   args.append("auth=(user, pword)")
    r = func(uri, **args)
    responseDictionary = r.json()
    #If API call errors out print the error and quit the script
    if r.status_code != 200:
      if 'errors' in responseDictionary:
        errors = responseDictionary.pop('errors')
        firstError = errors.pop()
      elif 'error' in responseDictionary:
        firstError = responseDictionary.pop('error')
      else:
        firstError['message'] = "No error message provided by response"
      print("{0} returned an error, exiting the script.\n   Status Code: {1} \n Error: {2}".format(name, r.status_code , firstError['message']))
      return False
    else:
      return responseDictionary

class Settings(object):

  def __init__(self, currentDir = ""):
    if not currentDir:
      currentDir = os.path.dirname(os.path.realpath(__file__))
    self._settings = currentDir
    self._model = {}

  @property
  def _settings(self):
      return self.__settings
  @_settings.setter
  def _settings(self, value):
    self.__settings = {}
    packageDefaultYaml = os.path.dirname(os.path.realpath(__file__))
    packageDefault = open(packageDefaultYaml + '/settings/default.yaml', 'r')
    self.__settings =  yaml.load(packageDefault)
    packageDefault.close()
    ## this will load a Plugins default settings
    if not packageDefaultYaml == value:
      default = open(value + '/settings/default.yaml', 'r')
      self.__plugin =  yaml.load(default)
      default.close()
      self.__settings = dict(self.__settings.items() + self.__plugin.items())
    path = __name__
    localFile = expanduser('~') + '/.' + '/'.join(path.split('.')) + '.yaml'
    # If there is an override file in the home dir (ex. ~/.drupdates/utils.yaml)
    if os.path.isfile(localFile):
      local = open(localFile, 'r')
      self.__local =  yaml.load(local)
      local.close()
      self.__settings = dict(self.__settings.items() + self.__local.items())

  @property
  def _model(self):
      return self.__model
  @_model.setter
  def _model(self, value = {}):
    value['default'] = ''
    value['value'] = ''
    value['prompt'] = ''
    value['format'] = ''
    value['null'] = ''
    self.__model = value

  def get(self, setting):
    if setting in self._settings:
      settingComplete = dict(self._model.items() + self._settings[setting].items())
      if not settingComplete['value'] and not settingComplete['null']:
        value = raw_input(settingComplete['prompt'] + ":")
        self.set(setting, value, settingComplete)
      else:
        return settingComplete['value']
    else:
      return ""

  def set(self, setting, value, complete):
    # FIXME: need better format parsing (ie int, boolean, dict, list etc...)
    if complete['format'] == 'list':
      value = value.split()
    elif complete['format'] == 'dict':
      import json
      value = json.loads(value)
    self.__settings[setting]['value'] = value

class Plugin(Settings):

  def __init__(self):
    self.PluginFolder = os.path.dirname(os.path.realpath(__file__)) + "/plugins"
    self.MainModule = "__init__"
    self._plugins = ""

  @property
  def PluginFolder(self):
      return self._PluginFolder
  @PluginFolder.setter
  def PluginFolder(self, value):
      self._PluginFolder = value

  @property
  def MainModule(self):
      return self._MainModule
  @MainModule.setter
  def MainModule(self, value):
      self._MainModule = value

  @property
  def _plugins(self):
      return self.__plugins
  @_plugins.setter
  def _plugins(self, value):
      self.__plugins = self.getPlugins()

  """
  Simple Plugin system shamelessly based on:
  http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
  """
  def getPlugins(self):
    plugins = {}
    possibleplugins = os.listdir(self.PluginFolder)
    for i in possibleplugins:
      location = os.path.join(self.PluginFolder, i)
      if not os.path.isdir(location) or not self.MainModule + ".py" in os.listdir(location):
        continue
      info = imp.find_module(self.MainModule, [location])
      plugins[i] = ({"name": i, "info": info})
    return plugins

  def loadPlugin(self, plugin):
    return imp.load_module(self.MainModule, *plugin["info"])
