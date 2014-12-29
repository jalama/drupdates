#!/usr/bin/env python

import json
from drupdates.utils import *
from drupdates.datastores import *

data = datastores('')
settings = data.dbSettings()

print json.dumps(settings._settings)
