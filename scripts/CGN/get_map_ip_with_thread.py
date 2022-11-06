#!/usr/bin/python3
""" This Script is Getting the Private or Public IP of IP List from A10 devices using threading
Input Parameters:
    USERNAME: the username used to connect to A10 devices
    PASSWD: the password used to connect to A10 devices
    DEBUG: send debug as true to display more information about the process
        - admins use this for extra troubleshooting
Input CSV File:
    IPS_FILE_PATH File Example
        IP Address,     Time,                   Port
        5.6.12.0,    "06/02/2019 13:01:57",  53532
        7.12.120.7,  "06/02/2019 13:01:57",  4518
        5.2.118.108,  "06/02/2019 13:01:57",  40162
        17.25.8.35,    "06/02/2019 13:01:57",  43952

    python get_map_ip_with_thread.py
    python get_map_ip_with_thread.py --debug
Output:
    Example:

"""
import sys
import argparse
from typing import List, Tuple, Any
from os import path, listdir
from os.path import isfile, join

from threading import Thread

sys.path.append('..')
#pylint: disable=wrong-import-position
from CGN.cgnat_base import CgnatBaseClass
from config import FILES_PATH, SHORT_ACTIVE_CGNAT_DEVICES_WITH_HOST, PREFIX_PRIVATE
from common.log_extender import log_to_console
from common.authenticate import credential
from models.a10_models import IPMappingModel
from common.pandas_extender import read_and_validate_csv, save_data_frame_to_csv
#pylint: enable=wrong-import-position

def str_to_int_or_zero(value):
    """ Convert value to Int if not possible return 0 """
    try:
        value = int(value)
    except ValueError:
        value = 0
    return value

def read_csv_file() -> Tuple[bool, str | Any]:
    """ Get the details of the CSV file """
    ## validate if the file exist with correct name in correct path
    file_name = 'cgnat_owner_ips.csv'
    file_path = path.join(FILES_PATH, '')
    files = [f for f in listdir(file_path) \
        if isfile(join(file_path, f)) and f.endswith(file_name)]
    if len(files) != 1:
        return False, "You should upload file with name "+ file_name + " to this " + file_path

    ## Validate & Load the csv file
    # Main column name of the CSV file
    csv_header_list = ['IP Address', 'Port', 'Time']
    file_full_path = path.join(file_path, file_name)
    is_success, imported_csv = read_and_validate_csv(file_full_path, csv_header_list, "Set Of")
    imported_csv['pd_index'] = imported_csv.reset_index().index
    return is_success, imported_csv

def get_distinct_ip_list(csv_data) -> List[IPMappingModel]:
    """ Get Distinct Rows from DataFrame Depend on passed columns """
    search_ip_list: List[IPMappingModel] = []
    for _, row in csv_data.iterrows():
        search_ip = str(row['IP Address'].strip())
        search_port = str_to_int_or_zero(row['Port'])
        rows = [f for f in search_ip_list \
            if str(f.search_ip) == search_ip and \
                str_to_int_or_zero(f.search_port) == search_port]
        if len(rows) < 1:
            search_ip_list.append(
                IPMappingModel(
                    search_ip=search_ip,
                    search_port=search_port
                )
            )
    return search_ip_list

def get_map_ips_of_search_list(cgn_device,
    user_name, passwd, ip_map_result, indx, search_list: List[IPMappingModel], debug):
    """ Get private IPs of search IP and Port List """
    try:
        device_ip = cgn_device[0].strip()
        cgnat_obj = CgnatBaseClass(device_ip=device_ip,
            username=user_name,
            passwd=passwd,
            debug=debug
        )
        is_success, result = cgnat_obj.get_ip_details_list(search_list=search_list, prefixes=PREFIX_PRIVATE)
        if not is_success:
            # log_to_console("", result)
            return False, "Error Occur While Retrive the IP, check console logs"

        for res in result:
            # Check if the output has correct values about one of the search ips
            if "NAT IP Address:" in str(res.output.strip()) and \
                "Inside User:" in str(res.output.strip()):

                # get the search ip and port that internal ip found
                search_ip = str(res.command).rsplit(' ', 2)[1]
                search_port = str(res.command).rsplit(' ', 2)[2].strip()
                search_port = "0" if search_port == "port-mapping" else search_port
                found_ips = []
                # print(str(res.command).rsplit(' ', 2)[1], \
                #  str(res.command).rsplit(' ', 2)[2].strip())
                # print(str(res.output.strip()))

                # extract the found ip or found ips from the output
                output_lines = str(res.output.strip()).splitlines()
                grap_inside_user_lines = [f for f in output_lines if f.startswith("Inside User:")]
                # print(grap_inside_user_lines)
                for line in grap_inside_user_lines:
                    found_ips.append(line.split()[-1])

                # add the found ip to the corresponding search list index
                # *Note: here the search items reference to the original search_list
                # this means any change in it will reflect to the values of the original list
                search_items = [f for f in search_list if str(f.search_ip) == str(search_ip) \
                    and str(f.search_port) == str(search_port)]
                if len(search_items) >= 1:
                    for ser_item in search_items:
                        ser_item.found_ip = found_ips

        result_list = []
        for itm in search_list:
            if itm.found_ip != "":
                result_list.append(itm)

        ip_map_result[indx] = result_list
    except Exception as ex:
        log_to_console("Error Occur: ", ex)

def get_distinct_map_result(ip_map_list) -> List[IPMappingModel]:
    """ Get Distinct Rows from DataFrame Depend on passed columns """
    result: List[IPMappingModel] = []
    for itms in ip_map_list:
        for itm in itms:
            rows = [f for f in result \
                if str(f.search_ip) == str(itm.search_ip) and \
                    str_to_int_or_zero(f.search_port) == str_to_int_or_zero(itm.search_port)]
            if len(rows) == 0:
                result.append(itm)
    return result

def merge_last_result_to_original_data(map_result: List[IPMappingModel], csv_df_list):
    """ Merge the result of the map ips with the original csv provided """
    # Check if there is column called result in csv object or not
    is_result_exist = [f for f in list(csv_df_list.columns) if str(f).lower() == "result"]
    if len(is_result_exist) < 1:
        csv_df_list["Result"] = ''

    for itm in map_result:
        csv_df_list['Result'] = csv_df_list.apply(lambda row, item = itm: \
            ','.join(str(e) for e in item.found_ip) \
            if row['IP Address'] == item.search_ip
                and str_to_int_or_zero(row['Port']) == str_to_int_or_zero(item.search_port) \
            else row['Result'], axis=1)

    return csv_df_list

def main_function(user_name, passwd, debug):
    """ The main entry point of the script """
    # Read the CSV file in File Path or in Default Path
    is_success, ip_list = read_csv_file()
    if not is_success:
        print(ip_list)

    # Get Distinct IP and Ports from the provided csv file
    filtered_ip_list: List[IPMappingModel] = get_distinct_ip_list(ip_list)

    # Get The Owner IPs from CGN devices
    threads: List[Thread] = []
    ip_map_results: List[IPMappingModel] = [{} for x in SHORT_ACTIVE_CGNAT_DEVICES_WITH_HOST]
    for index, cgn_device in enumerate(SHORT_ACTIVE_CGNAT_DEVICES_WITH_HOST):
        process = Thread(target=get_map_ips_of_search_list,
            args=(cgn_device, user_name, passwd, ip_map_results, index, filtered_ip_list, debug))
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

    # Get Final Distinct List of Search List with Found IPs
    ## the result is coming from the 10 devices so there is repetation so we need to get the
    ## filtered list with exact results from the 10 devices
    ip_map_results = get_distinct_map_result(ip_map_results)

    # Add the result to the Original CSV
    final_ip_list = merge_last_result_to_original_data(ip_map_results, ip_list)

    # Save the dataframe in CSV file
    final_ip_list = final_ip_list.drop("pd_index", axis=1)
    file_name = 'cgnat_owner_ips_output.csv'
    file_path = path.join(FILES_PATH, '')
    file_full_path = path.join(file_path, file_name)
    save_data_frame_to_csv(final_ip_list, file_full_path)

    print(final_ip_list)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="This script is used to get the owner ip for FMS ticket")

    # define options you need to provide to the script
    parser.add_argument("--debug", "-d",
        dest="debug", action="store_true",
        default=False, help="Pass true or false")

    args = parser.parse_args(sys.argv[1:])
    # args.beautify = str2bool(args.beautify)

    username, password = credential()
    main_function(username, password, args.debug)
