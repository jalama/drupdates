import datetime, requests, os, imp, yaml, urlparse, subprocess
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
    r = func(uri, **args)
    try:
      responseDictionary = r.json()
    except ValueError:
      return r
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

  def sysCommands(self, object, phase = ''):
    """ Run a system command based on the subprocess.popen method.
    For example maybe you want a symbolic link, on a unix box,
    from /opt/drupal to /var/www/drupal you would add the command(s)
    to the appropriate phase setting in you yaml settings files.

    Note: the format of the setting is a multi-dimensional list

    Example (form sitebuild.build():
      postBuildCmds:
        value:
          -
            - ln
            - -s
            - /var/www/drupal
            - /opt/drupal

    Note: You can refer to an attribute in the calling class, assuming they are
    set, by prefixing them with "att_" in the settings yaml above,
    ex. att_siteDir would pass the sitebuild.siteDir attribute

    Keyword arguments:
    phase -- the phase the script is at when sysCommands is called (default "")
    object -- the object the call to sysCommand is housed within
    """
    commands = self.settings.get(phase)
    if commands and type(commands) is list:
      for command in commands:
        if type(command) is list:
          # Find list items that match the string after "att_",
          # these are names names of attribute in the calling class
          for key, item in enumerate(command):
            if item[:4] == 'att_':
              attribute = item[4:]
              try:
                command[key] = getattr(object, attribute)
              except AttributeError:
                continue
          try:
            popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          except OSError as e:
            print "Cannot run {0} the command doesn't exist, \n Error: {1}".format(command.pop(0), e.strerror)
          stdout, stderr = popen.communicate()
          if stderr:
            print "There was and issue running {0}, \n Error: {1}".format(command, stderr)
        else:
          continue

  def aliases(self):
    """ Build a Drush alias file in $HOME/.drush, with alises to be used later

    Notes:
    The file name is controlled by the drushAliasFile settings
    All of the aliases will be prefixed with "drupdates" if he default file name
      is retained
    """

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
    """ Clean-up the alias files crreated by aliases method

    """
    if os.path.isfile(self._aliases['file']):
      os.remove(self._aliases['file'])
      os.remove(self._aliases['folder'] + "/settings.py")
      return True
    else:
      return False

class Plugin(Settings):

  """
  Simple Plugin system shamelessly based on:
  http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
  """

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
