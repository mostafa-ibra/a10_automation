#!/usr/bin/python3
"""
    This Script is extending the functionality of panda library
"""

from os import path
from os.path import exists, join

import pandas as pd
import numpy as np

class PandasExtender:
    """ This class wrap the functions related to pandas """

    def __init__(self):
        pass

def read_csv(path_to_csv):
    """ read CSV file """
    #Check if the file exist on hard disk or not
    if not exists(path_to_csv):
        return False, "Error: CSV file not exist in specified path : " + path_to_csv
    # Read the file lines and store it on imported_csv variable
    imported_csv = pd.read_csv(path_to_csv)
    return True, imported_csv

def read_and_validate_csv(path_to_csv, header_check_list, validate_option):
    """ Read CSV File and make sure the header is same as header_check_list
    @Input:
        header_check_list: List of headers like ['Network', 'Subnet'] """
    is_readed, imported_csv = read_csv(path_to_csv)

    if not is_readed:
        return False, imported_csv

    # get the head (column names) of the csv file
    input_header_file = list(imported_csv.columns.values)
    # remove leading and trailing spaces from every string in the list
    input_header_file = [x.strip(' ') for x in input_header_file]

    # Compare the Current Header and Expected Header
    # if set(header_check_list) <= set(input_header_file):
        # return True, imported_csv
    if validate_option == "Equal":
        if set(header_check_list) != set(input_header_file):
            return False, "Header of CSV file should be like this : " + str(header_check_list)
    if validate_option == "Set Of":
        if not (set(header_check_list) &
            set(input_header_file) == set(header_check_list)):
            return False, "Header of CSV file should contain this : " + str(header_check_list)

    return True, imported_csv

def save_data_frame_to_csv(data_frame, csv_destination_file):
    """ Store the Dataframe in CSV format with file name stored in 'csv_destination_file' """
    data_frame.to_csv (csv_destination_file, index = None, header=True)
    return True, True
    