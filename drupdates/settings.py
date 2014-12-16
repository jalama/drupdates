import os
from os.path import expanduser
import yaml

class Settings:
    
	__localFile = expanduser("~") + '/.drupdates/main.yaml'

	def __init__(self):
		if os.path.isfile(self.__localFile):
			stream = open(self.__localFile, 'r')
			self.__settings =  yaml.load(stream)
			stream.close()

	def get(self, setting):
		return self.__settings[setting]['value']

