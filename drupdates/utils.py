import datetime, requests, os, imp, yaml, urlparse
from drupdates.settings import *
from os.path import expanduser


class utils(object):

  def __init__(self):
    self.settings = Settings()
    self.aliases()

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

  def aliases(self):
    ret = False
    aliasFileName = self.settings.get('drushAliasFile')
    drushFolder = expanduser('~') + '/.drush'
    drushFile = drushFolder + "/" + aliasFileName
    if os.path.isfile(drushFile):
      ret = True
    else:
      if not os.path.isdir(drushFolder):
        try:
          os.makedirs(drushFolder)
        except OSError as e:
          print "Could not create ~/.drush folder \n Error: {0}".format(e.strerror)
      currentDir = os.path.dirname(os.path.realpath(__file__))
      # Symlink the Drush aliases file
      src = currentDir + "/scripts/" + aliasFileName
      try:
        os.symlink(src, drushFile)
        ret = True
      except OSError as e:
        print "Could not create Drush alias file \n Error: {0}".format(e.strerror)
      # Symlink the settings file used by above Drush aliases file
      src = currentDir + "/scripts/settings.py"
      dst = drushFolder + "/settings.py"
      try:
        os.symlink(src, dst)
        ret = True
      except OSError as e:
        print "Could not create settings.py file \n Error: {0}".format(e.strerror)
    self._aliases = {"folder" : drushFolder, "file" : drushFile}

  def deleteFiles(self):
    if os.path.isfile(self._aliases['file']):
      os.remove(self._aliases['file'])
      os.remove(self._aliases['folder'] + "/settings.py")
      return True
    else:
      return False

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
