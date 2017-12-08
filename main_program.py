#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '2'

"""
  Author:  Ross <peregrine.warren@physics.ox.ac.uk>
           Adapted from code by Ivan Ramirez <ivanrafaelramirez@gmail.com>
  Purpose: Main program for inSitu ECHO control. This creates and controls the threads and GUI.
  Last updated: 01/06/17
"""

import os
import sys
import datetime
import getpass
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import numpy as np
import pandas as pd

from src.inficon_engine import * # inficon engine (imports inficon drivers)
from src.measurement_engine import * # conductivity engine (import Keithley drivers)
from src.insitu_ECHO_GUI_2 import * # GUI design created QtDesigner
import src.Utilities as Utilities # utilities file mainly for handling fmf format

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class programSetup(QObject):

    # Define unbound signal as class attribute 
    signalStatus = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent) # inheriting from QApplication but doesn't referene it as parent=None
        
        # Create a GUI object.self = __main__,programSetup
        self.gui = mainWindow()
        
        # Setup the worker object and the worker_thread.
        self.worker1 = keithleyWorker() 
        self.worker_thread1 = QThread()
        
        self.worker2 = inficonWorker() 
        self.worker_thread2 = QThread()        
        
        # Move worker object to worker thread and start worker_thread.
        self.worker1.moveToThread(self.worker_thread1)
        self.worker_thread1.start()
        
        self.worker2.moveToThread(self.worker_thread2)
        self.worker_thread2.start()        
        
        # Make any cross object connections.
        self._connectSignals()
        
        self.gui.show()
        
    def _connectSignals(self): 
        # Keithley connections
        self.gui.mainWindow.start_button.clicked.connect(self.gui.getInputs) # get inputs before running work
        self.gui.mainWindow.start_button.clicked.connect(self.worker1.startWork) # run worker
        self.gui.mainWindow.stop_button.clicked.connect(self.forceWorkerReset1)
        self.gui.mainWindow.pushButtonSave.clicked.connect(self.gui.selectFile)   
        self.gui.mainWindow.actionSave_settings.triggered.connect(self.gui.getInputs)
        self.gui.mainWindow.actionLoad_settings.triggered.connect(self.gui.restoreState)
        # Save signals
        self.worker1.endData.connect(self.gui.saveData)
        self.worker1.beginData.connect(self.gui.createSaveDatabase)
        self.worker1.newfixedVDataPoint.connect(self.gui.plotPoint)
        self.worker1.appendData.connect(self.gui.appendSaveDatabase)
        self.worker1.newIVData.connect(self.gui.plotIV)           
        self.signalStatus.connect(self.gui.updateStatus)
        # Inficon connections
        self.gui.mainWindow.pushButton_QCMStart.clicked.connect(self.gui.getInputs) # get inputs before running work
        self.gui.mainWindow.pushButton_QCMStart.clicked.connect(self.worker2.startWork)
        self.gui.mainWindow.pushButton_QCMStop.clicked.connect(self.forceWorkerReset2)
        self.worker2.endDepositionData.connect(self.gui.saveDepositionData)
        self.worker2.newDepositionDataPoint.connect(self.gui.plotDepositionPoint)
        #General GUI connections
        self.worker1.signalStatus.connect(self.gui.updateStatus)
        self.worker2.signalStatus.connect(self.gui.updateStatus)
        self.worker2.InficonConsole.connect(self.gui.writeInficonConsole)
        self.worker1.KeithleyConsole.connect(self.gui.writeKeithleyConsole)
        self.parent().aboutToQuit.connect(self.forceQuit)

        
    def forceWorkerReset1(self):
        if self.worker_thread1.isRunning():
            self.worker1.stopWork()
            self.signalStatus.emit('Keithley thread: Idle')
            
    def forceWorkerReset2(self):
        if self.worker_thread2.isRunning():
            self.worker2.stopWork()
            self.signalStatus.emit('Inficon thread: Idle')
            
            
    def forceQuit(self):
        '''If parent is QApplication is killed (window closed) this shutdown the threads'''
        if self.worker_thread1.isRunning():
            self.worker1.stopWork()
            #time.sleep(0.3) 
            self.worker_thread1.exit()
        if self.worker_thread2.isRunning():
            self.worker2.stopWork()
            #time.sleep(0.3) 
            self.worker_thread2.exit()
            
            
            
class keithleyWorker(QObject):
    '''IV data aquisition worker'''
    
    KeithleyConsole = pyqtSignal(str)
    signalStatus = pyqtSignal(str)
    endData = pyqtSignal(object)
    beginData = pyqtSignal(object)
    appendData = pyqtSignal(object)
    newfixedVDataPoint = pyqtSignal(object)
    newIVData = pyqtSignal(object)
    askParameters = pyqtSignal(object)    
    
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        
    @pyqtSlot()        
    def startWork(self):
        
        self._flag = False
        self.user_parameters = pd.DataFrame.from_csv('src/df_measurement.csv', header=1) # Get input parameters from df_measurement
        smu, rm = IV_Engine.connect2Keith(self)
        
        if self.user_parameters.value['takeIVsweep'] == 'True':
            v, i = IV_Engine.measure_IVsweep(self, smu)
        
        if self.user_parameters.value['takefixedV'] == 'True':
            v, i = IV_Engine.measure_fixedV(self, smu)
        
        if self.user_parameters.value['takefixedI'] == 'True':
            v, i = IV_Engine.measure_fixedI(self, smu)        
        
        self.KeithleyConsole.emit('# Measurement thread idle #')
        self.signalStatus.emit('Measurement thread idle')
    
    @pyqtSlot()
    def stopWork(self):
        self._flag = True
        
        
class inficonWorker(QObject):
    
    signalStatus = pyqtSignal(str)
    InficonConsole = pyqtSignal(str)
    endDepositionData = pyqtSignal(object)
    newDepositionDataPoint = pyqtSignal(object)
    #askParameters = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        
    @pyqtSlot()        
    def startWork(self):
        self._flag = False
        self.signalStatus.emit('Inficon thread running...')
        self.user_parameters = pd.DataFrame.from_csv('src/df_measurement.csv', header=1) # Get input parameters from df_measurement
        thickness = inficon_engine.monitor_QCM(self, self.user_parameters.loc['inficonAddr'].value)
        self.InficonConsole.emit('Thickness monitoring complete.')
        
    @pyqtSlot()
    def stopWork(self):
        self._flag = True
    

class mainWindow(QMainWindow):
    '''Main applicaiton window'''
    
    signalStatus = pyqtSignal(str)

    def __init__(self, parent = None):
        
        ### QTDESIGNER MADE GUI ###
        super(mainWindow, self).__init__(parent)
        self.mainWindow = Ui_MainWindow()
        self.mainWindow.setupUi(self)
        self.setUpPlot()
        #sys.stdout = EmittingStream(textWritten=self.write) #redirect console print to UI
        
        ### Widget and fmf definitions ###
        self.inputManager = pd.DataFrame.from_csv('src/df_template.csv', header=1) # object for metadata
        fields = list(self.inputManager.index) # create a list of the indices in the metadata file
        self.inputWidgets = [w for w in self.findChildren(QWidget) if str(w.accessibleName()) in fields] # creates list of all QWidgets in GUI        
        
        
    @pyqtSlot(str)
    def updateStatus(self, status):
        self.mainWindow.statusbar.showMessage(status)
        
        
    @pyqtSlot(str)
    def writeKeithleyConsole(self, s):
        '''write text to text slot in UI'''
        self.mainWindow.plainTextEdit.moveCursor(QTextCursor.End)
        self.mainWindow.plainTextEdit.ensureCursorVisible()
        self.mainWindow.plainTextEdit.insertPlainText(s)
        self.mainWindow.plainTextEdit.insertPlainText('\n')
        
    @pyqtSlot(str)
    def writeInficonConsole(self, s):
        '''write text to Inficon text slot in UI'''
        self.mainWindow.plainTextEdit_2.moveCursor(QTextCursor.End)
        self.mainWindow.plainTextEdit_2.ensureCursorVisible()
        self.mainWindow.plainTextEdit_2.insertPlainText(s) 
        self.mainWindow.plainTextEdit_2.insertPlainText('\n')
        
    @pyqtSlot(object)
    def getInputs(self):
        '''get measurement parameters from GUI and store in dataframe.'''
        # Get widget values and units
        for w in self.inputWidgets:
            try:
                self.inputManager.loc[str(w.accessibleName())].value = Utilities.getWidgetValue(w)
                
                # Get units for certain measurement parameters
                if '_units' in str(w.accessibleName()):
                    self.inputManager.loc[str(w.accessibleName())].value = Utilities.getWidgetUnits(w)
            except:
                print ('Input parameter error: ', w.objectName())
            
        
        self.inputManager.loc['date'].value = str(datetime.datetime.now())
        self.inputManager.loc['user'].value = str(getpass.getuser())
        self.inputManager.loc['vers'].value = __version__
        
        if self.mainWindow.checkBox_IV.isChecked() == True and self.mainWindow.checkBox_fixedV.isChecked() == True :
            raise Exception('One measurement ONLY')
        if self.mainWindow.checkBox_IV.isChecked() == True and self.mainWindow.checkBox_fixedI.isChecked() == True :
            raise Exception('One measurement ONLY')
        if self.mainWindow.checkBox_fixedV.isChecked() == True and self.mainWindow.checkBox_fixedI.isChecked() == True :
            raise Exception('One measurement ONLY')
        if self.mainWindow.checkBox_IV.isChecked() == True and self.mainWindow.checkBox_fixedV.isChecked() == True and self.mainWindow.checkBox_fixedI.isChecked() == True:
            raise Exception('One measurement ONLY')        
        
        if self.mainWindow.checkBox_IV.isChecked() == True:
            self.inputManager.loc['setup'].value = str('IVsweep')
            self.inputManager.loc['fixedV'].value = None
            self.inputManager.loc['nRepeatsV'].value = None
            self.inputManager.loc['pauseTimeV'].value = None
            self.inputManager.loc['fixedI'].value = None
            self.inputManager.loc['nRepeatsI'].value = None
            self.inputManager.loc['pauseTimeI'].value = None            
          
        if self.mainWindow.checkBox_fixedV.isChecked() == True: 
            self.inputManager.loc['setup'].value = str('FixedV')
            self.inputManager.loc['fixedI'].value = None
            self.inputManager.loc['nRepeatsI'].value = None
            self.inputManager.loc['pauseTimeI'].value = None              
            self.inputManager.loc['initialV'].value = None
            self.inputManager.loc['finalV'].value = None
            self.inputManager.loc['stepSize'].value = None           
            self.inputManager.loc['holdTime'].value = None            
            self.inputManager.loc['x_descript'].value = str('Voltage')            
            self.inputManager.loc['x_descript'].units = str('[V]')
            self.inputManager.loc['y_descript'].value = str('Current')            
            self.inputManager.loc['y_descript'].units = str('[A]')            
        
        if self.mainWindow.checkBox_fixedI.isChecked() == True: 
            self.inputManager.loc['setup'].value = str('FixedI')
            self.inputManager.loc['fixedV'].value = None
            self.inputManager.loc['nRepeatsV'].value = None
            self.inputManager.loc['pauseTimeV'].value = None              
            self.inputManager.loc['initialV'].value = None
            self.inputManager.loc['finalV'].value = None
            self.inputManager.loc['stepSize'].value = None           
            self.inputManager.loc['holdTime'].value = None            
            self.inputManager.loc['y_descript'].value = str('Voltage')            
            self.inputManager.loc['y_descript'].units = str('[V]')
            self.inputManager.loc['x_descript'].value = str('Current')            
            self.inputManager.loc['x_descript'].units = str('[A]')               
            
        if self.mainWindow.checkBox_IV.isChecked() == False and self.mainWindow.checkBox_fixedV.isChecked() == False and self.mainWindow.checkBox_fixedI.isChecked() == False:
            self.inputManager.loc['setup'].value = str('DepositionMonitoring')
            self.inputManager.loc['fixedV'].value = None
            self.inputManager.loc['nRepeatsV'].value = None
            self.inputManager.loc['pauseTimeV'].value = None
            self.inputManager.loc['fixedI'].value = None
            self.inputManager.loc['nRepeatsI'].value = None
            self.inputManager.loc['pauseTimeI'].value = None
            self.inputManager.loc['initialV'].value = None
            self.inputManager.loc['finalV'].value = None
            self.inputManager.loc['stepSize'].value = None           
            self.inputManager.loc['holdTime'].value = None            
            self.inputManager.loc['x_descript'].value = str('Time')  
            self.inputManager.loc['x_descript'].units = str('s')
            self.inputManager.loc['y_descript'].value = str('QCM1 thickness, QCM1 rate, QCM2 thickness, QCM2 rate, etc.')                
            self.inputManager.loc['y_descript'].units = str('')           
            
        if self.inputManager.loc['exp_name'].value == '':
            self.inputManager.loc['exp_name'].value = ' '
    
            
        if self.inputManager.loc['sample'].value == '':
            self.inputManager.loc['sample'].value = ' '
            
        if self.inputManager.loc['sav_loc'].value == '':
            self.inputManager.loc['sav_loc'].value = os.getcwd()         
            
        mainWindow.saveState(self)
        
        
    @pyqtSlot()
    def saveState(self):
        ''' Save current inputs to csv '''
        try:
            hdr =  ' --- Insitu ECHO meas template for data-frame used to store inputs and write file header - change at your own risk---,,,,'
            with open('src/df_measurement.csv','w') as f:
                f.write(hdr + '\n')
            self.inputManager.to_csv('src/df_measurement.csv', mode = 'a', na_rep = ' ') #append (hdr)
        except:
            print ('Settings NOT saved. Please check df_template status.')

    @pyqtSlot()
    def restoreState(self):
        ''' write inputManager values to user input widgets.
                input widget values saved on close to inputManager csv'''
        try:
            self.inputManager = pd.DataFrame.from_csv('src/df_measurement.csv', header = 1)
            for w in self.inputWidgets:
                field = w.accessibleName()
                #if not (str(field) == 'exp_name' or str(field) == 'sample') or '_units' not in str(field):
                if '_units' not in str(field):
                    if self.inputManager.loc[field].value != None and self.inputManager.loc[field].value != ' ':
                        Utilities.setWidgetValue(w, self.inputManager.loc[field].value)
                if '_units' in str(field):
                    Utilities.setWidgetUnits(w, self.inputManager.loc[field].value)
                    
        except:
            print ('Settings reload: Failed at widget %s' % (field))           
        
    @pyqtSlot(object)
    def createSaveDatabase(self):
        self.fname = Utilities.save_to_file(self.inputManager, [], []) #pass no data to save an initial file with correct headers etc
    
    @pyqtSlot(object)    
    def appendSaveDatabase(self, datPoint):
        Utilities.append_save_to_file(self.fname, datPoint[1], datPoint[2])    
 
    @pyqtSlot(object)
    def saveData(self, dat):
        '''Save final data array'''
        if self.mainWindow.checkBoxSave.isChecked():
            if self.mainWindow.checkBox_IV.isChecked():
                fname = Utilities.save_to_file(self.inputManager, dat[0], dat[1])              

        else:
            print ('### Data has not been saved. ###')
            
    @pyqtSlot(object)
    def saveDepositionData(self, dat):
        '''Save final data array'''
        if self.mainWindow.checkBoxSave.isChecked():
            Utilities.deposition_save_to_file(self.inputManager, dat[0], dat[1], dat[2], dat[3], dat[4], dat[5], dat[6], dat[7], dat[8])
        else:
            print ('### Data has not been saved. ###')    

            
    @pyqtSlot()
    def selectFile(self):
        '''Directory browser on gui.
        Only allow user to choose directory. avoids idiocy'''
        try:
            current = self.mainWindow.lineEditSave.text()
            self.mainWindow.lineEditSave.setText(QFileDialog(directory = current).getExistingDirectory()+'/')
        except Exception:
            self.mainWindow.lineEditSave.setText(QFileDialog().getExistingDirectory()+'/')
            
            
        
    @pyqtSlot(object)    
    def plotPoint(self, datPoint):
        '''Update GUI graph with new IV measurement point and append to save file'''
        self.fixedVfig.plot(datPoint[0],datPoint[2])
        self.fixedVfig.figure.suptitle('Fixed Voltage/Current Measurements')
        self.fixedVfig.axes.set_xlabel('Sample')
        self.fixedVfig.axes.set_ylabel('I [A] / V [V]')
        self.mainWindow.pltWidget.figure.tight_layout()
        self.mainWindow.pltWidget.draw()
        
    @pyqtSlot(object)    
    def plotDepositionPoint(self, datPoint):
        '''Update GUI graph with new deposition measurement point'''
        if (self.mainWindow.comboBoxQCM_Display.currentText() == 'Thickness'):
            self.depositionfig.plot(datPoint[0],datPoint[1], 'rs', datPoint[0],datPoint[3], 'bs', datPoint[0],datPoint[5], 'gs', datPoint[0],datPoint[7], 'ys',)
            self.depositionfig.figure.suptitle('Thickness Monitor')
            self.depositionfig.axes.set_xlabel('Time (s)')
            self.depositionfig.axes.set_ylabel('Thickness (Angstroms)')
            self.mainWindow.pltWidget_2.figure.tight_layout()
            self.mainWindow.pltWidget_2.draw()
        if (self.mainWindow.comboBoxQCM_Display.currentText() == 'Rates'):
            self.depositionfig.plot(datPoint[0],datPoint[2], 'r--', datPoint[0],datPoint[4], 'b--', datPoint[0],datPoint[6], 'g--', datPoint[0],datPoint[8], 'y--',)
            self.depositionfig.figure.suptitle('Rate Monitor')
            self.depositionfig.axes.set_xlabel('Time (s)')
            self.depositionfig.axes.set_ylabel('Rate (Angstroms/sec)')
            self.mainWindow.pltWidget_2.figure.tight_layout()
            self.mainWindow.pltWidget_2.draw()        
        
        
        
    @pyqtSlot(object)    
    def plotIV(self, datPoint):
        '''Update GUI graph with new measurement point'''
        self.IVfig.plot(datPoint[0],datPoint[1])
        self.IVfig.figure.suptitle('IV plot')
        self.IVfig.axes.set_xlabel('Voltage [V]')
        self.IVfig.axes.set_ylabel('I (A)')
        self.mainWindow.pltWidget.figure.tight_layout()
        self.mainWindow.pltWidget.draw()        


    def setUpPlot(self):
        '''Create matplotlib in main window'''
        # Conductivity plot
        embeddedGraph = self.mainWindow.pltWidget
        self.fixedVfig = embeddedGraph.figure.add_subplot(111)
        self.IVfig = self.mainWindow.pltWidget.figure.add_subplot(111)
        embeddedGraph.figure.tight_layout()
        self.mainWindow.toolbar = NavigationToolbar(embeddedGraph,self)
        self.mainWindow.plotLayout.addWidget(self.mainWindow.toolbar)
        
        # Deposition Plot
        embeddedGraph2 = self.mainWindow.pltWidget_2
        self.depositionfig = embeddedGraph2.figure.add_subplot(111)
        embeddedGraph2.figure.tight_layout()
        self.mainWindow.toolbar2 = NavigationToolbar(embeddedGraph2,self)
        self.mainWindow.plotLayout_2.addWidget(self.mainWindow.toolbar2)        
        
        
class EmittingStream(QObject):
    '''object for print to gui'''
    
    textWritten = pyqtSignal(str)
    
    def write(self, text):
        self.textWritten.emit(str(text))
        
    def flush(self):
        '''system.stdout must be replaced with file-like object,
        therefore we include the flush method'''
        pass
        
    
        
def main():
    qt_app = QApplication([]) # create an instance of class QApplication
    win = programSetup(qt_app) # create an instance of programSetup inheriting from QApplication
    qt_app.exec_() # start event loop of the QApplication

if __name__=='__main__':
    main()
    