#!/usr/bin/env python
#coding:utf-8
"""
  Author:   Ross <ross.warren@pm.me>
  Purpose:  Run to give monitor ECHO presure, src temp and rates.
  Created:  17/02/19
"""

from drivers.eurothermDriver import TCU
from drivers.inficonDriver import inficon310C
from drivers.pressureDriver import TPG261

import datetime
import csv
from time import sleep


# ----------------------------------------------------------------------
def makeConnections():
        """Make connections to all drives"""

        tempUnitConnectionPars = {
                "method": "rtu",
                "port": '/dev/ttyUSB0',
            "parity": 'E',
                          "baudrate": 9600,
                          "bytesize": 8
        }

        tempUnit = TCU(tempUnitConnectionPars)
        pressureUnit = TPG261(port='/dev/ttyUSB2')
        inficon = inficon310C(port='/dev/ttyUSB1')

        return tempUnit, pressureUnit, inficon


# ----------------------------------------------------------------------
def recordECHO(tcu, pcu, inf):
        """Continuosly check ECHO status"""

        # Path and filename of data
        now = datetime.datetime.now()
        path = 'saved-logs/'
        filename = str(str(now.date()) + '-' + str(now.hour) + '-' + str(now.minute) + '-ECHO-LOG.csv')

        # Create file and add header
        with open(str(path + filename), 'x') as f:
                writer = csv.writer(f)
                header = ['Sample', 'Temp 1', 'Temp 2', 'Temp 3', 'Rate 1', 'Rate 2', 'Rate 3', 'Thick 1', 'Thick 2', 'Thick 3', 'Pressure']
                writer.writerow(header)

        sample = 0
        sample_max = 21600  # 12 hours taking recordings every 2 secs

        print ('\n')
        print ('-' * 124)
        print ('{:>4}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}'.format(
                'Time', 'Temp 1', 'Temp 2', 'Temp 3', 'Rate 1', 'Rate 2', 'Rate 3', 'Thick 1', 'Thick 2', 'Thick 3', 'Pressure'))

        print ('-' * 124)

        try:
                # while un-interrupted by the keyboard, record the following data
                while sample < sample_max:
                        t1 = float(tcu.read_T(1))				# Temperature channel 1
                        t2 = float(tcu.read_T(2))				# Temperature channel 2
                        t3 = float(tcu.read_T(3))				# Temperature channel 3
                        i1 = float(inf.rate(1))					# Inficon channel 1
                        i2 = float(inf.rate(2))					# Inficon channel 2
                        i3 = float(inf.rate(3))					# Inficon channel 3
                        th1 = float(inf.thickness(1))			        # Inficon channel 1
                        th2 = float(inf.thickness(2))			        # Inficon channel 2
                        th3 = float(inf.thickness(3))			        # Inficon channel 3

                        try:
                                p = pcu.pressure_gauge(gauge=1)		        # Pressure
                        except IOError:
                                p = 1010                                        # Atmospheric pressure

                        print('{:>4}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12}'.format(sample, t1, t2, t3, i1, i2, i3, th1, th2, th3, p), end='\r')
                        log = [sample, t1, t2, t3, i1, i2, i3, th1, th2, th3, p]
                        
                        # Append readings to log file
                        with open(str(path + filename), 'a') as f:
                                writer = csv.writer(f)
                                writer.writerow(log)

                        sample += 1
                        sleep(2)

        except KeyboardInterrupt:
                print('\nInterrupted!\n')

        print('\nLogfile saved:', path, filename)


if __name__ == "__main__":
        tcu, pcu, inf = makeConnections()
        recordECHO(tcu, pcu, inf)
