""" Print report to the screen. """
from drupdates.constructors.reports import Report
from drupdates.settings import DrupdatesError
from drupdates.utils import Utils
import os

class File(Report):
    """ Print plugin to screen. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file = current_dir + '/settings/default.yaml'
        self.settings = Settings()
        self.settings.add(settings_file)

    def send_message(self, report_text):
        """ Write the file to the disk. """

        filename = self.settings.get('fileName')
        directory = self.settings.get('folderName')
        directory = Utils.detect_home_dir(directory)
        fullpath = os.path.join(directory, filename)
        try:
            default = open(fullpath, 'w')
        except IOError as error:
            msg = "Can't open reporting file, {0}".format(fullpath)
            raise DrupdatesError(20, msg)
        with open(fullpath, 'w') as outfile:
            outfile.write(report_text)
        print("Report written to {0}.".format(fullpath))
