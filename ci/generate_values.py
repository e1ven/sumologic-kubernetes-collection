#!/usr/bin/env python3

import argparse
import json
import re
import sys
import os

import yaml
from yaml.loader import SafeLoader

DESCRIPTION = "test"


def get_values(indent, data):
    return_value = []
    if 'properties' in data:
      for key, value in data['properties'].items():
        commented = ''
        if 'comment' in value:
          for line in value['comment'].split('\n'):
            if not line.strip():
              return_value.append(f"{indent}##")
            else:
              return_value.append(f"{indent}## {line}")
        if 'commented' in value and value['commented']:
          commented = '# '
        if 'properties' in value:
          return_value.append(f"{indent}{commented}{key}:")
        elif 'items' in value:
          return_value.append(f"{indent}{commented}{key}:")
          for item in value['items']:
            commented = ''
            if 'commented' in item and item['commented']:
              commented = '# '
            if 'comment' in item:
              for line in item['comment'].split('\n'):
                if '#' in indent:
                  return_value.append(f"{indent.replace('# ', '##')} {line.rstrip()}")
                else:
                  return_value.append(f"{indent}## {line.rstrip()}")
            dumped = yaml.dump(item['default']).strip()
            first = True
            for line in dumped.split("\n"):
              if first:
                return_value.append(f"{indent}{commented}- {line}")
                first = False
                continue
              return_value.append(f"{indent}{commented}  {line}")
        else:
          dumped = yaml.dump({key: value['default']}).strip()
          for line in dumped.split("\n"):
            if not line.strip():
              return_value.append(f"{indent}{commented.rstrip()}")
            else:
              return_value.append(f"{indent}{commented}{line.rstrip()}")
        if 'example' in value:
          dumped = yaml.dump({key: value['example']}).strip()
          for line in dumped.split("\n")[1:]:
            if not line.strip():
              return_value.append(f"{indent}#")
            else:
              return_value.append(f"{indent}# {line}")
        return_value += get_values(f"{indent}{commented}  ", data['properties'][key])
    return return_value

def main(schema, directory):
    with open(schema) as f:
        data = json.loads(f.read())
        values = ['## Sumo Logic Kubernetes Collection configuration file',
'## All the comments start with two or more # characters'] + get_values('', data)

    print('\n'.join(values))

    # with open(os.path.join(directory, "_values.yaml"), "w") as f:
    #   f.write(yaml.dump(values))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = sys.argv[0],
        description = DESCRIPTION)
    parser.add_argument('--schema', required=True)
    parser.add_argument('--dir', required=True)
    parser.add_argument('--full-diff', required=False, action='store_true')
    args = parser.parse_args()

    main(args.schema, args.dir)
