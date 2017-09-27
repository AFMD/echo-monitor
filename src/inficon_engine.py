'''
Methods and classes used for controlling the inficon. Driver in separate file.
'''

from src.inficon_control import *
import numpy as np
import time

class inficon_engine():
    """
    Engine for measurment loops and interfacing the GUI
    """
    
    def __init__(self):
        """Things that go first"""
        pass
        
    def monitor_QCM(self, addr):
        '''Continously probes thickness and rates of selected channels until cancel button is clicked'''
        
        self.inficon = inficon310C(port=addr)
        self.InficonConsole.emit('Monitoring film thickness...')
        self.signalStatus.emit('Monitoring film thickness...')
        QCM1_thickness = []
        QCM1_rate = []
        QCM2_thickness = []
        QCM2_rate = []
        QCM3_thickness = []
        QCM3_rate = []
        QCM4_thickness = []
        QCM4_rate = []
        data = []
        sampletime = []
        samplenumber = 0
        
        if (self.user_parameters.value['QCM1'] == 'True'): 
            self.InficonConsole.emit('Monitoring Channel 1: <Red>')
        if (self.user_parameters.value['QCM2'] == 'True'): 
            self.InficonConsole.emit('Monitoring Channel 2: <Blue>')            
        if (self.user_parameters.value['QCM3'] == 'True'): 
            self.InficonConsole.emit('Monitoring Channel 3: <Green>')    
        if (self.user_parameters.value['QCM4'] == 'True'): 
            self.InficonConsole.emit('Monitoring Channel 4: <Yellow>')  
        
        # Measurement loop
        while self._flag == False:
            if (self.user_parameters.value['QCM1'] == 'True'):
                QCM1_thickness1 = self.inficon.thickness(channel=1)
                QCM1_rate1 = self.inficon.rate(channel=1)
                QCM1_thickness.append(float(QCM1_thickness1))
                QCM1_rate.append(float(QCM1_rate1))
            if (self.user_parameters.value['QCM1'] == 'False'):
                QCM1_thickness.append(None)
                QCM1_rate.append(None)
            if (self.user_parameters.value['QCM2'] == 'True'):
                QCM2_thickness1 = self.inficon.thickness(channel=2)
                QCM2_thickness.append(float(QCM2_thickness1))
                QCM2_rate1 = self.inficon.rate(channel=2)
                QCM2_rate.append(float(QCM2_rate1))  
            if (self.user_parameters.value['QCM2'] == 'False'):
                QCM2_thickness.append(None)
                QCM2_rate.append(None)             
            if (self.user_parameters.value['QCM3'] == 'True'):
                QCM3_thickness1 = self.inficon.thickness(channel=3)
                QCM3_thickness.append(float(QCM3_thickness1))
                QCM3_rate1 = self.inficon.rate(channel=3)
                QCM3_rate.append(float(QCM3_rate1))  
            if (self.user_parameters.value['QCM3'] == 'False'):
                QCM3_thickness.append(None)
                QCM3_rate.append(None)              
            if (self.user_parameters.value['QCM4'] == 'True'):
                QCM4_thickness1 = self.inficon.thickness(channel=4)
                QCM4_thickness.append(float(QCM4_thickness1))
                QCM4_rate1 = self.inficon.rate(channel=4)
                QCM4_rate.append(float(QCM4_rate1))  
            if (self.user_parameters.value['QCM4'] == 'False'):
                QCM4_thickness.append(None)
                QCM4_rate.append(None)                

            elif(self.user_parameters.value['QCM1'] == 'False' and self.user_parameters.value['QCM2'] == 'False' and self.user_parameters.value['QCM3'] == 'False' and self.user_parameters.value['QCM4'] == 'False'):
                self.InficonConsole.emit(str('NO QCM CHANNEL SELECTED'))
                self._flag = True

            sampletime.append(samplenumber*float(self.user_parameters.value['QCM_sampleTime']))
            data = sampletime, QCM1_thickness, QCM1_rate, QCM2_thickness, QCM2_rate, QCM3_thickness, QCM3_rate, QCM4_thickness, QCM4_rate
            self.newDepositionDataPoint.emit(data) # for live update 
            time.sleep(float(self.user_parameters.value['QCM_sampleTime']))
            samplenumber += 1
        
        self.endDepositionData.emit(data)
        
        