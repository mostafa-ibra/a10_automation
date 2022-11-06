#!/usr/bin python3
"""
This Script is used to Manage Logging to console
"""
import json

def __obj_dict(obj):
    """
    Default DOC
    """
    return obj.__dict__

def log_to_console(output_name, output_value):
    """ used in debugging mode to display extra actions """
    print('Log: ' + output_name + ": ")
    print(output_value)

def log_object_to_console(obj_value, is_display_object_only=True, output_name=''):
    """ used in debugging custom class objects or list of it """
    if not is_display_object_only:
        print('Displaying ' + output_name + ": ")
    json_string = json.dumps(obj_value, default=__obj_dict)
    print(json_string)
