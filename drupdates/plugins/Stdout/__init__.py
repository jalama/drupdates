""" Print report to the screen. """
from drupdates.constructors.reports import Report

class Stdout(Report):
    """ Print plugin to screen. """

    def send_message(self, report_text):
        """ Print the report to the screen, or stdout."""
        print(report_text)
