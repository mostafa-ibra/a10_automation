#!/usr/bin python3
""" This Script Collect all Models related to F5 Devices """

class OutputCommands:
    """ This Model Represent the output of running one or multiple commands"""
    def __init__(self, command, output):
        self.command = command
        self.output = output
