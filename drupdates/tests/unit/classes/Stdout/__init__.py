""" Print report to the screen. """
from drupdates.constructors.reports import Report

class Druptest(Report):
    """ Print plugin to screen. """

    def send_message(self, report_text):
        """ Print the report to the screen, or stdout."""
        report_text = "Drupdtest {0}".format(report_text)
        print(report_text)
