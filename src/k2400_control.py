#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Code for controlling the Keithley2400. Code taken from Ivan's TPV setup: 
https://github.com/AFMD/transients
'''

import visa
import sys
import numpy as np

#defaultstdout = sys.stdout #save default console print location

class k2400():
	'''Class to control keithley SMU'''
	
	def __init__(self, rm, connectionPars):
		'''Connect to the Keithley?'''
		self.inst = k2400.inst_connect(rm, connectionPars)
		
		
	def inst_connect(rm, connectionPars):
		'''function to return a pyvisa Resource given some pars currently only works for serial'''
		
		try:
			if str(connectionPars.value['connectionType']) == 'Serial':
				baudR = int(connectionPars.value['baudR'])
				termChar = connectionPars.value['termChar']
				address = 'ASRL%s::INSTR' %(connectionPars.value['connectionAddr'])
				inst = rm.open_resource(address)
				inst.read_termination = k2400.input2unicode(termChar) #needs to be unicode, cf getwidgetValue
				inst.baud_rate = baudR
				return inst

			elif str(connectionPars.value['connectionType']) == 'GPIB':
				address = 'GPIB%s::%s::INSTR'%(connectionPars['gpibPrefix'], connectionPars['gpibAd'])
				inst = rm.open_resource(address)
		
		except:	
			raise Exception('Connection @ %s cannot be made.' %connectionPars.value['connectionAddr'])
	
	def input2unicode(s):
		s = s.replace('\\r','\r')
		s = s.replace('\\n','\n')
		return s #unicode(s) does not work here?	
		
	def connect_SMU(connSet):
		'''Method to connect to keithley'''
		rm = visa.ResourceManager('@py') #use py-visa backend
		smu = k2400(rm, connSet)
		return smu, rm		

	def write(self, s):
		'''Standard pyvisa write no added debug'''
		self.inst.write(s)

	def query(self, s):
		'''Standard pyvisa query no added debug'''
		a = self.inst.query(s)
		return a

	
	def measV(self, pars):
		'''take a current measurement at fixed voltage V'''
		self.write(':SYST:BEEP:STAT OFF') #TURN OFF annoying beeb
		self.write("SYST:RSEN %s"%pars['4wire']) #4 wire measurement or two wire?
		self.write(':TRIG:COUN 1')	#set to output 1 pulse
		self.write(':SOUR:FUNC VOLT')	#SELECT SOURCE
		self.write(':SENS:FUNC:CONC OFF') #do not measure both V and I concurrently
		self.write(':SENS:FUNC "CURR"') #Choose current measurement function
		self.write(':SOUR:VOLT:MODE FIXED') #fixed voltage source mode
		self.write(':SOUR:VOLT:RANG:AUTO ON') #auto range for voltage
		self.write(':SOUR:VOLT:LEV %s'%pars['fixedV']) #choose voltage for measurement
		self.write(':SENS:CURR:PROT 1E%s'%pars['complianceI']) # Sets compliance for measurement
		self.write(':SENS:NPLC %s'%pars['integrationTime']) # Sets integration time for measurement
		self.write(':SENS:CURR:RANG:AUTO ON') #Autorange for current measuremnet
		self.write(':FORM:ELEM VOLT,CURR') #voltage and current reading
		self.write(':OUTP ON')
		#print(self.query(':READ?'))
		v, i =[float(x) for x in self.query('READ?').split(',')] #break data str into values
		
		if pars['constantV'] == True:	# Keep supply on if checkbox is ticked otherwise turn off
			pass
		elif pars['constantV'] == False:
			self.write('OUTP OFF')
			
		return v, i
	
	def measI(self, pars):
		'''Push current I and measure voltage'''
		self.write(':SYST:BEEP:STAT OFF') #TURN OFF annoying beeb
		self.write("SYST:RSEN %s"%pars['4wire']) #4 wire measurement or two wire?
		self.write(':TRIG:COUN 1')	#set to output 1 pulse
		self.write(':SOUR:FUNC CURR')	#SELECT SOURCE
		#self.write(':SENS:FUNC:CONC OFF') #do not measure both V and I concurrently
		self.write(':SOUR:CURR:MODE FIXED') #fixed CURRENT source mode
		self.write(':SOUR:CURR:RANG:AUTO ON') #auto range for CURRENT
		self.write(':SOUR:CURR:LEV %s'%pars['fixedI']) #choose CURRENT for measurement
		self.write(':SENS:VOLT:PROT 1E%s'%pars['complianceV']) # Sets compliance for measurement
		self.write(':SENS:NPLC %s'%pars['integrationTime']) # Sets integration time for measurement
		self.write(':SENS:FUNC "VOLT"') #Choose VOLTAGE measurement function
		self.write(':SENS:VOLT:RANG:AUTO ON') #Autorange for VOLTAGE measuremnet
		self.write(':FORM:ELEM CURR,VOLT') #voltage and current reading
		self.write(':OUTP ON')
		#print(self.query(':READ?'))
		v, i =[float(x) for x in self.query('READ?').split(',')] #break data str into values
		
		if pars['constantI'] == True:	# Keep supply on if checkbox is ticked otherwise turn off
			pass
		elif pars['constantI'] == False:
			self.write('OUTP OFF')
		
		return i, v	
	
	def measIVsweep(self, pars):
		'''make an IV sweep'''
		self.write(':SYST:BEEP:STAT OFF') #TURN OFF annoying beeb
		self.write("ROUTe:TERM %s"%pars['route']) #select front/rear channel
		self.write("SENS:FUNC:CONC OFF") # measure only sens not sour
		self.write("SYST:RSEN %s"%pars['4wire']) #4 wire measurement or two wire?
	
		self.write("SOUR:FUNC VOLT")    #voltage source function
		self.write("SENS:FUNC 'CURR:DC'") #current sense function
		self.write("SENS:CURR:PROT 1E%s"%pars['complianceI'])    # current compliance in A
		self.write("SENS:NPLC %s"%pars['integrationTime']) # Sets integration time for measurement
	
		if float(pars['initialV'])<float(pars['finalV']):
			Vstep = float(pars['stepSize']) * 1
		else: 
			Vstep = float(pars['stepSize']) * -1
	
		#Sweep Settings: sweep structure seems to trig, delay, trig delay
		self.write("SOUR:VOLT:STARt %s"%pars['initialV']) # in V 
		self.write("SOUR:VOLT:STOP %s"%pars['finalV']) # in V
		self.write("SOUR:VOLT:STEP %s"%Vstep) # in V       
		self.write("SOUR:DEL %s"%pars['holdTime']) # delay in s

		self.write("TRIG:COUN %s"%self.query("SOUR:SWE:POIN?")) # set trigger to number of points in sweep
		self.write("SOUR:VOLT:MODE SWE")    #select voltage sweep mode
		
		self.write("SOUR:SWE:RANG AUTO")    #Auto source ranging
		self.write("SOUR:SWE:SPAC LIN")    #linear sweep
		
		self.write("SOUR:SWE:DIR UP")
		
		self.write("FORM:ELEM VOLT,CURR") #configure what READ will return, RES problematic
	
		#measure
		self.write("OUTP ON")    #turns on SMU at SOUR:VOL:STARtrig
		# READtriggers sweep (INIT) + (FETCH) data
		self.query('*OPC?') #check op complete
		data = np.fromstring(self.query("READ?"), sep =',') #convert str to np.array
		i_data = data[1::2]
		v_data = data[::2]
		self.write('OUTP OFF')
		
		return v_data,i_data 	
