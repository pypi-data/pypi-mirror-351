'''
Python macro for testing yaml files with given schema defined in json language.

usage: python3 test_schema.py file_to_be_tested.yaml schema.json
'''

import sys
import json
import yaml
from jsonschema import validate, ValidationError, FormatChecker

import datetime

def convert_dates(obj):
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(item) for item in obj]
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    return obj

with open(sys.argv[1]) as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

with open(sys.argv[2]) as stream:
    schema = json.load(stream)

try:  
    validate(instance=convert_dates(data), schema=schema, format_checker=FormatChecker())
except ValidationError as e:
    print(e.message)
