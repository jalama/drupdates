""" Utilities class providing useful functions and methods. """
import requests, os, subprocess, shutil
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from os.path import expanduser
from filecmp import dircmp
from drupdates.settings import Settings
from drupdates.settings import DrupdatesError
from drupdates.drush import Drush

class DrupdatesAPIError(DrupdatesError):
    """ Error thrown bu api_call. """

class Utils(object):
    """ Class of utilities used throughout the module. """

    def __init__(self):
        self.settings = Settings()

    @staticmethod
    def detect_home_dir(directory):
        """ If dir is relative to home dir rewrite as OS agnostic path. """
        parts = directory.split('/')
        if parts[0] == '~' or parts[0].upper() == '$HOME':
            del parts[0]
            directory = os.path.join(expanduser('~'), '/'.join(parts))
        return directory

    @staticmethod
    def remove_dir(directory):
        """ Try and remove the directory. """
        if os.path.isdir(directory):
            try:
                shutil.rmtree(directory)
            except OSError as error:
                msg = "Can't remove site dir {0}\n Error: {1}".format(directory, error.strerror)
                raise DrupdatesError(20, msg)
        return True

    def find_make_file(self, site_name, directory):
        """ Find the make file and test to ensure it exists. """
        make_format = self.settings.get('makeFormat')
        make_folder = self.settings.get('makeFolder')
        make_file = site_name + '.make'
        make_file_short = site_name
        if make_format == 'yaml':
            make_file += '.yaml'
            make_file_short += '.yaml'
        if make_folder:
            directory = os.path.join(directory, make_folder)
        file_name = os.path.join(directory, make_file)
        file_name_short = os.path.join(directory, make_file_short)
        if os.path.isfile(file_name):
            return file_name
        if os.path.isfile(file_name_short):
            return file_name_short
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
        method -- HTTP method to use (default = 'get')
        kwargs -- dictionary of arguments passed directly to requests module method

        """
        # Ensure uri is valid
        if not bool(urlparse(uri).netloc):
            msg = ("Error: {0} is not a valid url").format(uri)
            raise DrupdatesAPIError(20, msg)
        func = getattr(requests, method)
        args = {}
        args['timeout'] = (10, 10)
        for key, value in kwargs.items():
            args[key] = value
        try:
            response = func(uri, **args)
        except requests.exceptions.Timeout:
            msg = "The api call to {0} timed out".format(uri)
            raise DrupdatesAPIError(20, msg)
        except requests.exceptions.TooManyRedirects:
            msg = "The api call to {0} appears incorrect, returned: too many re-directs".format(uri)
            raise DrupdatesAPIError(20, msg)
        except requests.exceptions.RequestException as error:
            msg = "The api call to {0} failed\n Error {1}".format(uri, error)
            raise DrupdatesAPIError(20, msg)
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
            raise DrupdatesAPIError(20, msg)
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
                        print(msg)
                    results = popen.communicate()
                    if results[1]:
                        print("Running {0}, \n Error: {1}".format(command, results[1]))
                else:
                    continue

    def rm_common(self, dir_delete, dir_compare):
        """ Delete files in dir_delete that are in dir_compare.

        Iterate over the sites directory and delete any files/folders not in the
        commonIgnore setting.

        keyword arguments:
        dir_delete -- The directory to have it's file/folders deleted.
        dir_compare -- The directory to compare dirDelete with.
        """
        ignore = self.settings.get('commonIgnore')
        if isinstance(ignore, str):
            ignore = [ignore]
        dcmp = dircmp(dir_delete, dir_compare, ignore)
        for file_name in dcmp.common_files:
            os.remove(dir_delete + '/' + file_name)
        for directory in dcmp.common_dirs:
            shutil.rmtree(dir_delete + '/' + directory)
