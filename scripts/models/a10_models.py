#!/usr/bin python3
""" This Script has all Models related to A10 Devices """

class CommandModel:
    """ This Model used to send multiple commands to A10 device """
    def __init__(self, cmd, wait_time=1, recive_data_legnth=500, need_output=False, is_more=False):
        self.cmd = cmd
        self.wait_time = wait_time
        self.recive_data_legnth = recive_data_legnth
        self.need_output = need_output
        self.is_more=is_more

    def __str__(self):
        return "Command: " + self.cmd + " -- wait time: " + self.wait_time + " -- recive data legnth: " + self.recive_data_legnth

class IPMappingModel:
    """ This class represent the mapping between public/private IP and the opposite """
    def __init__(self, search_ip, search_port, found_ip: str = "", cgnat_device_name: str = ""):
        self.search_ip = search_ip
        self.search_port = search_port
        self.found_ip = found_ip
        self.cgnat_device_name = cgnat_device_name
