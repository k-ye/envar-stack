#!python3

import os
import sys
import argparse
from pathlib import Path


_DEFAULT_STACK_STORAGE_DIR = os.path.join(str(Path.home()), '.envarstacks')
_VERBOSE = False


def _set_verbose(v):
  global _VERBOSE
  _VERBOSE = v


def vlog(*args):
  if _VERBOSE:
    print(*args)


def log_error(*args):
  print(*args, file=sys.stderr)


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('op', help='"push", "pop", "print"')
  parser.add_argument('stack_name', help='Name of this stack')
  parser.add_argument('-e', '--envs', nargs='+',
                      help='A list of environment variables to be pushed.')
  parser.add_argument('-v', '--verbose', action='store_true')
  return parser.parse_args()


def ensure_dir(dirname):
  if not os.path.exists(dirname):
    os.makedirs(dirname)


def _make_stack_path(stack_name):
  return os.path.join(_DEFAULT_STACK_STORAGE_DIR, stack_name + '.txt')


def _print_envs_or_die(stack_name, template='%s=%s'):
  stack_path = _make_stack_path(stack_name)
  if not os.path.isfile(stack_path):
    log_error('Cannot find stack=%s' % stack_name)
    sys.exit(1)
  print('# [stack=%s] Saved environment variables' % stack_name)
  with open(stack_path, 'r') as f:
    is_key = True
    k, v = None, None
    for line in f:
      line = line.strip()
      if is_key:
        k = line
      else:
        v = line
        print(template % (k, v))
      is_key = not is_key
    if not is_key:
      log_error('Cannot find value for env=%s' % k)
      sys.exit(1)
  return stack_path


def push_envs(stack_name, envs):
  envs.sort()
  stored_envs = []
  for ev_name in envs:
    ev_val = os.environ.get(ev_name, default='')
    stored_envs.append((ev_name, ev_val))

  stack_path = _make_stack_path(stack_name)
  if os.path.isfile(stack_path):
    log_error('Stack=%s already exists' % stack_name)
    sys.exit(1)

  ensure_dir(_DEFAULT_STACK_STORAGE_DIR)
  with open(stack_path, 'w') as f:
    for k, v in stored_envs:
      f.write(k + '\n')
      f.write(v + '\n')
  vlog('Pushed stack=%s' % stack_name)


def pop_envs(stack_name):
  stack_path = _print_envs_or_die(stack_name, template='export %s=%s')
  os.remove(stack_path)
  vlog('\nPopped stack=%s' % stack_name)


def print_envs(stack_name):
  _print_envs_or_die(stack_name)


def main():
  cmd_args = parse_args()
  op = cmd_args.op
  _set_verbose(cmd_args.verbose)
  if op == 'push':
    push_envs(cmd_args.stack_name, cmd_args.envs)
  elif op == 'pop':
    pop_envs(cmd_args.stack_name)
  elif op == 'print':
    print_envs(cmd_args.stack_name)
  else:
    log_error('Unkown op=%s' % op)
    sys.exit(1)


if __name__ == '__main__':
  main()
