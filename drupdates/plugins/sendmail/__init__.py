from drupdates.utils import *
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

class sendmail():

  def __init__(self):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)

  def sendMessage(self, reportText):
    """ Send the report via email using sendmail."""
    today = str(datetime.date.today())

    msg = MIMEText(reportText)
    msg["From"] = self.settings.get('reportSender')
    msg["To"] = self.settings.get('resportRecipient')
    msg["Subject"] = "Drupdates report {0}.".format(today)
    p = Popen(["sendmail", "-t"], stdin=PIPE)
    p.communicate(msg.as_string())

