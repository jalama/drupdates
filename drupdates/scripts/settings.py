#!/usr/bin/env python

import json
from drupdates.utils import *

settings = Settings()

print json.dumps(settings._settings)
