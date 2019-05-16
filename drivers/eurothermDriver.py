# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 15:50:08 2018
Descript:
    Python driver for the Creaphys TCU230S controller w
    abstract and practical functions
How to:
    connection requires RS485.
    typically this means a USB-RS485 adapter such as https://www.conrad.de/de/digitus-seriell-usb-adapter-1x-rs485-stecker-1x-usb-20-stecker-a-da-70157-1020913.html?WT.mc_id=google_pla&WT.srch=1&ef_id=WkzmFwAAANdQaDlo:20180627095536:s&gclid=EAIaIQobChMIvJ-v6snz2wIVlPhRCh1VHg5iEAQYASABEgLK8PD_BwE&hk=SEM&insert_kz=VQ&s_kwcid=AL!222!3!254339639507!!!g!!
    and installation of a driver for the chip
    then its plug and play! (but be careful of units. cf eurotherm manual)
    
resources:
    - Eurotherm 3216 manual chapter 15 (I have highlited passages of interest)
    - pymodbus docu/schneider electric modbus page
    - TCU 230 docu (less relevant)
    
use:
    import in main program
status:
    all functions tested except ramp rate
    need to deal with SBRoken 
    
@author: ira
CHANGES:
11/7/18 - adpated for python 3.6
        - separate out engine from driver
"""

# from __future__ import division #sensible division for integers

from pymodbus.pdu import ModbusRequest #TCU comm. superfluous?
from pymodbus.client.sync import ModbusSerialClient as ModbusClient #TCU comm
import time
import numpy as np
import matplotlib.pyplot as plt

class TCU():
    '''TCU control class
        Use hex(address) to get correct address'''
        
    __verbose__ = True
    
    def __init__(self, connectionPars, channels = [1,2,3]):
        '''constructor'''
    
        #insert some stuff to get byte settings for different parities
        self.channels = channels
        self.MB = ModbusClient(**connectionPars)
        # print("Connection opened")
        connection = self.MB.connect() #for activat40_FundedProjects/EU_SEPOMO/ProjectTeam/_scripts/automation_n_instrumentation/mtc_project/dev/tcu2-DD-rw.py', ion

        if not connection: 
            raise Exception('\n\t\t'+'!'*20+'\nERROR: Unable to connect to TCU'
                            +'\n\t\t'+'!'*20)
        else:
            pass
        #rint ("\tTCU Connection successful\n")
           
        #remote state of each channel. Important to return channels to manual mode at end
        self.remote = {
                        1 : False,
                        2 : False,
                        3: False}
        
        #conversion brings from physical units to eurotherm readable values
        self.commands = {
                "readSP":{"type" : "R", "address": 0x2, "conversion" : 0.1}, 
                "setRmSP":{"type" : "W", "address": 0x1a, "conversion" : 10, "help" : "Use implemented function"},
                "setRamp":{"type" : "W", "address": 0x23, "conversion" : 0.1 },
                "readRamp":{"type" : "W", "address": 0x23},
                }
    
        
        #now should do some stuff with the remote output power (278/79) to make it safe.
        # this could be setting it to 111/112

    def __del__(self):
        '''safely delete object'''
        for channel in self.channels:
            self.setRemote(channel, False)
        self.MB.close()       
        
        
    def exec_command(self, commandName, channel,  value =''):
        '''generic abstract command implementation for any function (just add to self.commands)
           value: for write in appropriate units, commandName: from self comannds'''
        
        command_ = self.commands[commandName]
        if command_['type'] == "W":
            val = value*command_["conversion"]
            self.MB.write_register(command_['address'], val, unit = channel)
        elif command_['type'] == "R":
            val = self.MB.read_holding_registers(command_['address'], unit = channel)
            val = val.getRegister(0)
            return val*command_["conversion"]


    def setRemote(self, channel, remoteSP=True):
        '''switch to remote mode SP. Adress 276'''
        self.MB.write_register(0x114, int(remoteSP), unit = channel)
        self.remote[channel] = bool(remoteSP)


    def set_TargetSP(self, channel, temp):
        '''Set target set point. Adress 2'''
        if not self.remote[channel]:
            self.setRemote(channel)        
        self.MB.write_register(0x2, temp, unit=channel)


    def set_altSP(self, channel, temp_inC):
        ''' Set the alternative set point 
        (SP1 but for remote coms). Address 26
        '''
        temp = temp_inC *10 #switch to eurotherm language
        if not self.remote[channel]:
            self.setRemote(channel)
        self.MB.write_register(0x1a, temp, unit=channel)
    

    def set_SP1(self, channel, temp_inC):
        '''temp in degree celcius, 1 decimal
            WARNING: Talks to SP1 - BAD PRACTICE SEE EUROTHERM MANUAL'''
        
        temp = int(temp_inC*10) #switch to eurotherm temperature format
        self.MB.write_register(0x18, temp, unit=channel)

    
    def read_T(self, channel):
        '''  Address 1  '''
        temp = self.MB.read_holding_registers(0x1, unit = channel)
        temp = temp.getRegister(0)/10
            
        return temp
    
    
    def read_powerOut(self, channel):
        '''read current power output parameter which can be used to calculate
        the current on the source provided conversion is known.
        In general 60.0 corresponds to 6A but this should be checked. Addresses
        4 and 5. Unclear which is better'''
        OP = self.MB.read_holding_registers(0x4, unit = channel)
        OP = OP.getRegister(0x4) / 100
        
        if __verbose__:
            print ("the power for unit %s is: %s"%(channel, OP))
            
        return OP

    
    def setRemoteSP(self,channel,temp):        
        self.exec_command('setRmSP',channel,temp)
        self.setRemote(channel)  
        #self.setRemote(channel, False)
        
if __name__ == "__main__":
        connectionPars = {
            "method": "rtu",
            "port": '/dev/ttyUSB0',
            "parity": 'E',
            "baudrate": 9600,
            "bytesize": 8
        }
        # Test open connection
        tcu = TCU(connectionPars)

        print ("Complete")
