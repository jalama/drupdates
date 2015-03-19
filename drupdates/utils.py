""" Utilities class providing useful functions and methods. """
import requests, os, imp, urlparse, subprocess, shutil, sys
from filecmp import dircmp
from drupdates.settings import Settings
from drupdates.drush import Drush


class Utils(object):
    """ Class of untilities used throughout the module. """

    def __init__(self):
        self.settings = Settings()

    @staticmethod
    def check_working_dir(directory):
        """ Ensure the directory is writable. """
        filepath = os.path.join(directory, "text.txt")
        try:
            open(filepath, "w")
        except IOError:
            sys.exit('Unable to write to directory {0} \n Exiting Drupdates'.format(directory))
            return False
        return True

    @staticmethod
    def remove_dir(directory):
        """ Try and remove the directory. """
        if os.path.isdir(directory):
            try:
                shutil.rmtree(directory)
            except OSError as error:
                print "Can't remove site dir {0}\n Error: {1}".format(directory, error.strerror)
                return False
        return True

    def find_make_file(self, site_name, directory):
        """ Find the make file and test to ensure it exists. """
        make_format = self.settings.get('makeFormat')
        make_folder = self.settings.get('makeFolder')
        make_file = site_name + '.make'
        if make_format == 'yaml':
            make_file += '.yaml'
        if make_folder:
            directory += '/' + make_folder
        file_name = directory + '/' + make_file
        if os.path.isfile(file_name):
            return file_name
        return False

    def make_site(self, site_name, site_dir):
        """ Build a webroot based on a make file. """
        web_root = self.settings.get('webrootDir')
        folder = os.path.join(site_dir, web_root)
        make_file = self.find_make_file(site_name, site_dir)
        Utils.remove_dir(folder)
        if make_file and web_root:
            # Run drush make
            # Get the repo webroot
            make_opts = self.settings.get('makeOpts')
            make_cmds = ['make', make_file, folder]
            make_cmds += make_opts
            make = Drush.call(make_cmds)
            return make

    @staticmethod
    def api_call(uri, name, method='get', **kwargs):
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
        func = getattr(requests, method)
        args = {}
        for key, value in kwargs.iteritems():
            args[key] = value
        response = func(uri, **args)
        try:
            response_dictionary = response.json()
        except ValueError:
            return response
        #If API call errors out print the error and quit the script
        if response.status_code not in [200, 201]:
            if 'errors' in response_dictionary:
                errors = response_dictionary.pop('errors')
                first_error = errors.pop()
            elif 'error' in response_dictionary:
                first_error = response_dictionary.pop('error')
            else:
                first_error['message'] = "No error message provided by response"
            msg = "{0} returned an error, exiting the script.\n".format(name)
            msg += "Status Code: {0} \n".format(response.status_code)
            msg += "Error: {0}".format(first_error['message'])
            print msg
            return False
        else:
            return response_dictionary

    def sys_commands(self, obj, phase=''):
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
        if commands and isinstance(commands, list):
            for command in commands:
                if isinstance(command, list):
                    # Find list items that match the string after "att_",
                    # these are names names of attribute in the calling class
                    for key, item in enumerate(command):
                        if item[:4] == 'att_':
                            attribute = item[4:]
                            try:
                                command[key] = getattr(obj, attribute)
                            except AttributeError:
                                continue
                    try:
                        popen = subprocess.Popen(command, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
                    except OSError as error:
                        msg = "Cannot run {0} the command doesn't exist,\n".format(command.pop(0))
                        msg += "Error: {1}".format(error.strerror)
                        print msg
                    results = popen.communicate()
                    if results[1]:
                        print "Running {0}, \n Error: {1}".format(command, results[1])
                else:
                    continue

    def rm_common(self, dir_delete, dir_compare):
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
        dcmp = dircmp(dir_delete, dir_compare, ignore)
        for file_name in dcmp.common_files:
            os.remove(dir_delete + '/' + file_name)
        for directory in dcmp.common_dirs:
            shutil.rmtree(dir_delete + '/' + directory)

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
