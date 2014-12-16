import subprocess
import json

def readUpdateReport(lst, updates = []):
  for x in lst:
    # build list of updates in a list,
    # when you hit a blank line you are done
    # note: if there are no updates the first line will be blank
    if not x == '':
      updates += x
    else:
      break

  return updates

def callDrush(commands, alias = '', jsonRet = False):
  """ Run a drush comand and return a list/dictionary of the results

  Keyword arguments:
  commands -- list containing command, arguments and options
  alias -- drush site alias of site where "commands" to run on
  json -- binary deermining if the given command can/should return json

  """
  # https://github.com/dsnopek/python-drush/, threw errors calling Drush()
  # consider --strict=no
  if not alias == '':
    commands.insert(0, '@' + alias)
  if jsonRet:
    commands.append('--format=json')
  commands.insert(0, 'drush')
  # run the command
  print commands
  popen = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = popen.communicate()
  if jsonRet:
    ret = json.loads(stdout)
  else:
    ret = stdout.split('\n')

  return ret

def importDrush(alias):
  """ Import a SQL dump using drush sqlc

  alias -- A Drush alias

  """
  commands = ['drush', '@' + alias, 'sqlc']
  popen = subprocess.Popen(cmds, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
  out, stderr = popen.communicate(file(backportDir + siteName + '.sql').read())
  if not stderr == '':
    print alias + " DB import error: " + stderr
    return False

  return True