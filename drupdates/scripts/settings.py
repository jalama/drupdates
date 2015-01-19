#!/usr/bin/env python

""" Publish the Datastore settings so the Drush alias file can read them."""
import json
from drupdates.utils import *
from drupdates.constructors.datastores import *

data = datastores()
settings = data.dbSettings()

print json.dumps(settings._settings)
