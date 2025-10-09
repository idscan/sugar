#!/usr/bin/env python3

# Copyright (c) 2013, Ruslan Baratov
# All rights reserved.

import argparse
import os
import re
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(
    description="""
        ios simulator launcher. Expected that application is gtest.
        If output is looks like passed test - exit with 0,
        otherwise exit with 1
        """
)

parser.add_argument(
    '--sim',
    type=str,
    required=True,
    help='full path to ios-sim'
)

parser.add_argument(
    '--target',
    type=str,
    required=True,
    help='name of target to launch'
)

parser.add_argument(
    '--args',
    type=str,
    nargs='*',
    help='arguments passed to application'
)

parser.add_argument(
    '--configuration',
    type=str,
    required=True,
    help='build configuration (e.g. Release, Debug)'
)

parser.add_argument(
    '--verbose',
    action='store_true',
    help='print a lot info'
)

parser.add_argument(
    '--devicetypeid',
    type=str,
    help='the type of the device simulator'
)

args = parser.parse_args()

class Log:
  def __init__(self):
    self.verbose = args.verbose
  def p(self, message):
    if self.verbose:
      print(message)

log = Log()

build_command = ['xcodebuild', '-sdk', 'iphonesimulator', '-arch', 'arm64']
build_command.append('-target')
build_command.append(args.target)
build_command.append('-configuration')
build_command.append(args.configuration)
subprocess.check_call(build_command)

application = '{}.app'.format(args.target)

def find_application(dir):
  for root, dirs, unused_filenames in os.walk(os.getcwd()):
    if not dir in dirs:
      continue
    walk_base = os.path.join(root, dir)
    for root_new, dirs_new, unused_filenames in os.walk(walk_base):
      if application in dirs_new:
        return os.path.join(root_new, application)
  message = '{} not found in {}'.format(application, dir)
  sys.exit(message)

app = find_application(args.configuration) # in old combined build scheme, used to append -iphonesimulator here

log.p('app found: {}'.format(app))

temp_dir = os.path.join(os.getcwd(), '__tmp_sim_logs__')
os.makedirs(temp_dir, exist_ok=True)

def try_run_simulator(application):
  cout_sim_log = tempfile.NamedTemporaryFile(
      delete=False, dir=temp_dir, suffix='.log', prefix='cout.'
  )

  cerr_sim_log = tempfile.NamedTemporaryFile(
      delete=False, dir=temp_dir, suffix='.log', prefix='cerr.'
  )

  log.p('log file: {}'.format(cout_sim_log.name))
  log.p('log file: {}'.format(cerr_sim_log.name))

  launch_command = [
      args.sim,
      '-a',
      application,
      '-o',
      cout_sim_log.name,
      '-e',
      cerr_sim_log.name,
  ]

  if args.devicetypeid:
    launch_command.append('-d')
    launch_command.append(args.devicetypeid)

  if args.args:
    launch_command.append('--args')
    for x in args.args:
      launch_command.append(x)

  subprocess.check_call(launch_command)

  cout_sim_log.close()
  cerr_sim_log.close()

  cout_data = open(cout_sim_log.name, 'r').read()
  cerr_data = open(cerr_sim_log.name, 'r').read()

  if len(cerr_data) != 0:
    message = 'Unexpected cerr output from {}:\n    {}\n'.format(
        application, cerr_data
    )
    sys.exit(message)

  if len(cout_data) == 0:
    sys.exit('output from {} is empty'.format(application))

  print(cout_data)

  if re.search('^ [1-9][0-9]* FAILED TEST$', cout_data, re.MULTILINE):
    return 1
  elif re.search('^\[  PASSED  \] [1-9][0-9]* tests?.$', cout_data, re.MULTILINE):
    return 0
  else:
    sys.exit("Can't find PASSED or FAILED test strings in output")

def run_simulator(application):
  retry_number = 3
  for i in range(retry_number):
    try:
      return try_run_simulator(application)
    except subprocess.CalledProcessError as exc:
      print('Run failed, retry ({} of {})'.format(i + 1, retry_number))
  sys.exit('Launch failed {} times'.format(retry_number))

result = run_simulator(app)
log.p('exit code: {}'.format(result))
sys.exit(result)
