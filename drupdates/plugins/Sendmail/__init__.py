""" Send report using sendmail. """
from drupdates.settings import Settings
from drupdates.constructors.reports import Report
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import datetime, os

class Sendmail(Report):
    """ sendmail report plugin. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file = current_dir + '/settings/default.yaml'
        self.settings = Settings()
        self.settings.add(settings_file)

    def send_message(self, report_text):
        """ Send the report via email using sendmail."""
        today = str(datetime.date.today())

        msg = MIMEText(report_text)
        msg["From"] = self.settings.get('reportSender')
        msg["To"] = self.settings.get('reportRecipient')
        msg["Subject"] = "Drupdates report {0}.".format(today)
        mail = Popen(["sendmail", "-t"], stdin=PIPE)
        mail.communicate(msg.as_string())

