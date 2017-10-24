#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Methods and classes used for conductivity measurements. Run in separate thread from GUI.
'''

import time
import random
import numpy as np

from src.k2400_control import * # conductivity engine controls keithley

class IV_Engine():
    '''Routine for fixed-voltage measurements and IV sweep'''
    def __init__(self, parent=None):
        #self._flag1 = False
        #sys.stdout = EmittingStream(textWritten=self.write) #redirect console print to UI
        pass
        
    def connect2Keith(self):
        smu, rm = k2400.connect_SMU(self.user_parameters)
        #print (smu.query('*IDN?'))
        return smu, rm
    
    def measure_fixedV(self, smu):
    
        self.KeithleyConsole.emit('Commencing fixed VOLTAGE measurements...')
        self.signalStatus.emit('Running fixed voltage measurement...')
        self.KeithleyConsole.emit('Sample \t Voltage [V] \t Current [A]')
        
        # Update measurement values with units
        self.user_parameters.value['fixedV'] = str(float(self.user_parameters.value['fixedV'])*float(self.user_parameters.value['fixedV_units']))
        
        v = []
        i = []
        t = []
        
        data = t, v ,i
        self.beginData.emit(data)
        
        for n in range ((int(self.user_parameters.value['nRepeatsV']))):
            if self._flag: 
                self.signalStatus.emit('Stopped.')
                self.KeithleyConsole.emit('Measurement aborted')
                return v, i
            vv, ii = smu.measV(self.user_parameters.value)
            self.KeithleyConsole.emit('%.4g \t %.4g\t %.4g' % (n, vv, ii))
            v.append(float(vv))
            i.append(float(ii))
            t.append(int(n))
            data = t, v, i
            # for continous save
            datPoint = n, vv, ii
            self.appendData.emit(datPoint)
            
            self.newfixedVDataPoint.emit(data) # for live update plus append save
            time.sleep(float(self.user_parameters.value['pauseTimeV'])) #Time between measurements
        data = t, v, i
        return v, i
    
    def measure_fixedI(self, smu):
    
        self.KeithleyConsole.emit('Commencing fixed CURRENT measurements...')
        self.signalStatus.emit('Running fixed CURRENT measurement...')
        self.KeithleyConsole.emit('Sample \t CURRENT [A] \t VOLTAGE [V]')
        
        # Update measurement values with units
        self.user_parameters.value['fixedI'] = str(float(self.user_parameters.value['fixedI'])*float(self.user_parameters.value['fixedI_units']))
        
        v = []
        i = []
        t = []
        
        data = t, v ,i
        self.beginData.emit(data)
        
        for n in range ((int(self.user_parameters.value['nRepeatsI']))):
            if self._flag: 
                self.signalStatus.emit('Stopped.')
                self.KeithleyConsole.emit('Measurement aborted')
                return v, i
            vv, ii = smu.measI(self.user_parameters.value)
            self.KeithleyConsole.emit('%.4g \t %.4g\t %.4g' % (n, vv, ii))
            v.append(float(vv))
            i.append(float(ii))
            t.append(int(n))
            data = t, v, i
            # for continous save
            datPoint = n, vv, ii
            self.appendData.emit(datPoint)
            
            self.newfixedVDataPoint.emit(data) # for live update plus save append
            time.sleep(float(self.user_parameters.value['pauseTimeI'])) #Time between measurements
        data = t, i, v
        return v, i    
    
    def measure_IVsweep(self, smu):
        
        self.KeithleyConsole.emit('Commencing IV Sweep...')
        
        v = []
        i = []
        if self._flag: 
            self.signalStatus.emit('Stopped.')
            self.KeithleyConsole.emit('Measurement aborted')
            return v, i
        v, i = smu.measIVsweep(self.user_parameters.value)
        data = v, i
        
        self.KeithleyConsole.emit('Voltage [V] \t Current [A]')
        for n in range(len(v)):
            self.KeithleyConsole.emit('%.4g \t %.4g' % (data[0][n], data[1][n]))
        
        self.newIVData.emit(data) # for graph update
        self.endData.emit(data)
        
        if self.user_parameters.value['takeIVreverse'] == True:
            
            self.KeithleyConsole.emit('Commencing Reverse Sweep...')
            
            v = []
            i = []
            if self._flag: 
                self.signalStatus.emit('Stopped.')
                self.KeithleyConsole.emit('Measurement aborted')
                return v, i
            v, i = smu.measIVsweep(self.user_parameters.value)
            data = v, i
            
            self.KeithleyConsole.emit('Voltage [V] \t Current [A]')
            for n in range(len(v)):
                self.KeithleyConsole.emit('%.4g \t %.4g' % (data[0][n], data[1][n]))
            
            self.newIVData.emit(data) # for graph update
            self.endData.emit(data)            
        
        return v, i    

        
class livePlot:
    '''Class for plotting the conductivity data live'''
    
    def __init__(self, parent=None, width =5, height=4, dpi=100):
        fig = Figure(figsize = (width,height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)
        self.initial_fig()
        
    
    def animatePlot(graph_data):
        ax1.clear()
        ax1.plot(data)
        
        
        
    
    

    
        