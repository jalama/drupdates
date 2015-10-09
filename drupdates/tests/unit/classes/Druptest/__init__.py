""" Print report to the screen. """
from drupdates.constructors.reports import Report

class Stdout(Report):
    """ Print plugin to screen. """

    def send_message(self, report_text):
        """ Print the report to the screen, or stdout."""
        report_text = "Druptest {0}".format(report_text)
        print(report_text)
