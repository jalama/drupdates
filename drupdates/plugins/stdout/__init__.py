from drupdates.utils import *
from drupdates.constructors.reports import *

class stdout(Reports):

  def sendMessage(self, reportText):
    """ Print the report to the screen, or stdout."""
    print reportText
