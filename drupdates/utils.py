import datetime
import requests
import os
from os.path import expanduser
import yaml

def nextFriday():
  # Get the data string for the following Friday
  today = datetime.date.today()
  if datetime.datetime.today().weekday() == 4:
    friday = str(today + datetime.timedelta( (3-today.weekday())%7+1 ))
  else:
    friday = str(today + datetime.timedelta( (4-today.weekday()) % 7 ))
  return friday

def apiCall (uri, name, method = 'get', **kwargs):
  #user = '', pword = ''):
  """ Perform and API call, expecting a JSON response.  Largely a wrapper
  around the request module

  Keyword arguments:
  uri -- the uri of the Restful Web Service (required)
  name -- the human readable label for the service being called (required)
  method -- HTTP method to use (defaul = 'get')
  kwargs -- dictionary of arguments passed directly to requests module method

  """
  # FIXME: need to HTML escape passwords
  func = getattr(requests, method)
  args = {}
  for key, value in kwargs.iteritems():
    args[key] = value
  # if not user == '' and not pword == '':
  #   args.append("auth=(user, pword)")
  r = func(uri, **args)
  responseDictionary = r.json()
  #If API call errors out print the error and quit the script
  if r.status_code != 200:
    if 'errors' in responseDictionary:
      errors = responseDictionary.pop('errors')
      firstError = errors.pop()
    elif 'error' in responseDictionary:
      firstError = responseDictionary.pop('error')
    else:
      firstError['message'] = "No error message provided by response"
    print("{0} returned an error, exiting the script.\n   Status Code: {1} \n Error: {2}".format(name, r.status_code , firstError['message']))
    return False
  else:
    return responseDictionary


class Settings:

  __localFile = expanduser("~") + '/.drupdates/main.yaml'

  def __init__(self):
    self.__settings = {}
    self.__model()
    currentDir = os.path.dirname(os.path.realpath(__file__))
    default = open(currentDir + "/settings/default.yaml", 'r')
    self.__settings =  yaml.load(default)
    default.close()
    if os.path.isfile(self.__localFile):
      local = open(self.__localFile, 'r')
      self.__local =  yaml.load(local)
      local.close()
      self.__settings = dict(self.__settings.items() + self.__local.items())

  def __model(self):
    model = {}
    model['default'] = ''
    model['value'] = ''
    model['prompt'] = ''
    model['format'] = ''
    self.__model = model

  def get(self, setting):
    if setting in self.__settings:
      setting = dict(self.__model.items() + self.__settings[setting].items())
    return setting['value']

# Load variables:
settings = Settings()
