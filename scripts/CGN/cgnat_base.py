#!/usr/bin/python
""" This Script is The Base of A10 Devices
Constructor Parameters:
    device_ip : IP of the A10 device
    username:
    passwd:
    debug:
Output:
    Example:
"""

import sys
from typing import List
sys.path.append("..")
from common.ssh_client_base import SshClientBaseClass
from models.a10_models import CommandModel, IPMappingModel

class CgnatBaseClass(SshClientBaseClass):
    """
    This Class connect to A10 and Get the Information
    """

    def __init__(self, device_ip, username, passwd, debug=False):
        super().__init__(device_ip, username, passwd, debug)

    def get_ip_details_list(self, search_list: List[IPMappingModel], prefixes):
        """
        Default DOC
        """
        commands = []
        try:
            commands.append(CommandModel("en\n"))
            commands.append(CommandModel("\n"))

            for item in search_list:
                prepare_command = "show cgnv6 fixed-nat " + ("inside-address " \
                        if (item.search_ip.startswith(tuple(prefixes))) \
                        else "nat-address ") + item.search_ip + " "
                prepare_command = prepare_command + ("port-mapping" \
                        if (item.search_port == 0) \
                        else str(item.search_port))
                prepare_command = prepare_command + "\n"
                commands.append(CommandModel(prepare_command, 4, 5000, True))

            is_success, outputs = self.run_commands(commands=commands)

        except Exception as ex_error:
            outputs = ex_error
            is_success = False

        self.close_connection()
        return is_success, outputs
