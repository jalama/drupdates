""" Utilities class providing useful functions and methods. """
import requests, os, imp, urlparse, subprocess, shutil, sys
from filecmp import dircmp
from drupdates.settings import Settings
from drupdates.drush import Drush


class utils(object):

  def __init__(self):
    self.settings = Settings()

  @staticmethod
  def check_working_dir(directory):
    filepath = os.path.join(directory, "text.txt")
    try:
     open(filepath, "w")
    except IOError:
      sys.exit('Unable to write to working directory {0} \n Exiting Drupdates'.format(directory))
      return False
    return True

  @staticmethod
  def removeDir(directory):
    """ Try and remove the directory. """
    if os.path.isdir(directory):
      try:
        shutil.rmtree(directory)
      except OSError as e:
        print "Cannot remove the site {0} directory\n Error: {1}".format(directory, e.strerror)
        return False
    return True

  def findMakeFile(self, siteName, directory):
    """ Find the make file and test to ensure it exists. """
    makeFormat = self.settings.get('makeFormat')
    makeFolder = self.settings.get('makeFolder')
    makeFile = siteName + '.make'
    if makeFormat == 'yaml':
      makeFile += '.yaml'
    if makeFolder:
      directory += '/' + makeFolder
    fileName = directory + '/' + makeFile
    if os.path.isfile(fileName):
      return fileName
    return False

  def makeSite(self, siteName, siteDir):
    """ Build a webroot based on a make file. """
    webRoot = self.settings.get('webrootDir')
    folder = os.path.join(siteDir, webRoot)
    makeFile = self.findMakeFile(siteName, siteDir)
    utils.removeDir(folder)
    if makeFile and webRoot:
      # Run drush make
      # Get the repo webroot
      makeOpts = self.settings.get('makeOpts')
      makeCmds = ['make', makeFile, folder]
      makeCmds += makeOpts
      make = Drush.call(makeCmds)
      return make

  @staticmethod
  def apiCall (uri, name, method = 'get', **kwargs):
    """ Perform and API call, expecting a JSON response.

    Largely a wrapper around the request module

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
    if r.status_code not in  [200, 201]:
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

    For example: maybe you want a symbolic link, on a unix box,
    from /opt/drupal to /var/www/drupal you would add the command(s)
    to the appropriate phase setting in you yaml settings files.

    Note: the format of the setting is a multi-dimensional list

    Example (from Sitebuild.build():
      postBuildCmds:
        value:
          -
            - ln
            - -s
            - /var/www/drupal
            - /opt/drupal

    Note: You can refer to an attribute in the calling class, assuming they are
    set, by prefixing them with "att_" in the settings yaml above,
    ex. att_site_dir would pass the Sitebuild.site_dir attribute

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

  def rmCommon(self, dirDelete, dirCompare):
    """ Delete files in dirDelete that are in dirCompare.

    keyword arguments:
    dirDelete -- The directory to have it's file/folders deleted.
    dirCompare -- The directory to compare dirDelete with.

    Iterate over the sites directory and delete any files/folders not in the
    commonIgnore setting.
    """
    ignore = self.settings.get('commonIgnore')
    if isinstance(ignore, str):
      ignore = [ignore]
    dcmp = dircmp(dirDelete, dirCompare, ignore)
    for fileName in dcmp.common_files:
      os.remove(dirDelete + '/' + fileName)
    for directory in dcmp.common_dirs:
      shutil.rmtree(dirDelete + '/' + directory)

class Plugin(object):
    """ Simple Plugin system.

    This is shamelessly based on:
    http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
    """

    def __init__(self):
        self._plugin_folder = os.path.dirname(os.path.realpath(__file__)) + "/plugins"
        self._main_module = "__init__"
        self._plugins = self.get_plugins()

    def get_plugins(self):
        """ Collect Plugins from the plugins folder. """
        plugins = {}
        possibleplugins = os.listdir(self._plugin_folder)
        for i in possibleplugins:
            location = os.path.join(self._plugin_folder, i)
            if not os.path.isdir(location) or not self._main_module + ".py" in os.listdir(location):
                continue
            info = imp.find_module(self._main_module, [location])
            plugins[i] = ({"name": i, "info": info})
        return plugins

    def load_plugin(self, plugin):
        """ Load an individual plugin. """
        return imp.load_module(self._main_module, *plugin["info"])
