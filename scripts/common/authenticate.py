#!/usr/bin/python3
""" This Script is contains all functions used in authentication
Output:
    Example:

"""

import getpass

def credential():
    """ Get username and password """

    # Capture username
    user = input('Enter Username: ')
    # Capture password
    pwd = getpass.getpass(f'{user}, enter your password: ')

    return user, pwd
