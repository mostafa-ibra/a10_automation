#!/usr/bin python3
"""This Script is used to communicate with devices
    Through SSH"""

import sys
import time
import paramiko
sys.path.append("..")
from models.device_models import OutputCommands
from common.log_extender import log_object_to_console, log_to_console

class SshClientBaseClass:
    """ 
    This is the base class for all functionalities with SSH Servers
    """

    remote_conn_pre = None
    remote_conn = None

    def __init__(self, device_ip, username, passwd, debug=False):
        self.__device_ip = str(device_ip)
        self.__username = username
        self.__password = passwd
        self.__port = 22
        self.debug = debug
        self.display_lines = []

    def get_device_ip(self):
        """ Return The value of Device IP
        """
        return self.__device_ip

    def connect_to_device(self):
        """
        Default DOC
        """
        try:
            if self.debug:
                log_to_console("try to connect to ", self.__device_ip)
                log_to_console('port:', self.__port)
                log_to_console('username:', self.__username)

            self.remote_conn_pre = paramiko.SSHClient()
            self.remote_conn_pre.load_system_host_keys()
            self.remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.debug:
                log_to_console("Connected Successfully ", '')

            self.remote_conn_pre.connect(self.__device_ip, port=self.__port, username=self.__username, password=self.__password)
            self.remote_conn = self.remote_conn_pre.invoke_shell()
            time.sleep(1)
            output = self.remote_conn.recv(1000)

            if self.debug:
                output = output.decode("utf-8")
                log_to_console("output of connect to device : ", output)

            return "connected"
        except Exception as error:
            log_to_console('error in connect to device with below error', error)
            self.close_connection()
            return "not connected"


    def run_command(self, command, wait_time=1, recive_data_legnth=500):
        """
        Default DOC
        """
        output = ''
        try:
            if self.remote_conn_pre is None:
                self.connect_to_device()

            if self.debug:
                log_to_console("send command to device", command)

            self.remote_conn.send(command)
            time.sleep(wait_time)
            output = self.remote_conn.recv(recive_data_legnth)
            output = output.decode("utf-8")
            self.close_connection()
        except Exception as error:
            log_to_console("Error occured: ", error)
            self.close_connection()

        return output

    def run_commands(self, commands):
        """
        Default DOC
        """
        outputs = []
        is_success = False
        try:
            if self.remote_conn_pre is None:
                self.connect_to_device()

            for obj in commands:
                self.remote_conn.send(obj.cmd)
                time.sleep(obj.wait_time)
                return_output = self.remote_conn.recv(obj.recive_data_legnth)

                if obj.need_output and obj.is_more:
                    ret_out = return_output.decode("utf-8").split("\r\n")
                    condition_while = ret_out[-1].lower()
                    while condition_while.endswith('--more--'):
                        ret_out = ret_out[:-1]
                        self.remote_conn.send(" ")
                        time.sleep(obj.wait_time)
                        return_output = self.remote_conn.recv(obj.recive_data_legnth)
                        ret_out2 = return_output.decode("utf-8").split("\r\n")
                        ret_out.extend(ret_out2)
                        condition_while = ret_out2[-1].lower()

                    output = OutputCommands(
                            command=obj.cmd,
                            output=ret_out
                        )
                    outputs.append(output)

                elif obj.need_output:
                    output = OutputCommands(
                        command=obj.cmd,
                        output=return_output.decode("utf-8")
                    )
                    outputs.append(output)

            is_success = True
            if self.debug:
                log_object_to_console(outputs)

        except Exception as ex_error:
            print(ex_error)
            outputs = ex_error
        finally:
            self.close_connection()

        return is_success, outputs

    def close_connection(self):
        """ Close the connection if it is still opened
        """
        if self.remote_conn_pre is not None:
            self.remote_conn_pre.close()
