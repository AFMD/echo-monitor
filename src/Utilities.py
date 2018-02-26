import visa
import pandas as pd
import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import sys
import glob
import serial
import math

def inst_autoFind(s, rm):
	''' Find instrument Address from IDN string 
	    - Fails for SERIAL (baudrate, par requ.)
	    - Fails if use multiple insts. of same kind.
	'''
	nonSerAds = [r for r in rm.list_resources() if r.find('ASRL') ==-1] #throw out serial addreses
	
	for resource in nonSerAds:
		try: 
			idn = rm.open_resource(resource).query('*IDN?')
			if idn.find(s)>=0:
				print('Connected to device %s at Address %s'%(idn, resource))
				return resource
		except Exception:
			print('Error attempting to connect to inst address %s'%resource)
			print('TraceBack: %s'%sys.exc_info())
			return 0

	#failed:
	print('Error: auto-discovery of %s failed, make sure instrument is connected'%s)

def filterDf(inptdf):
	''' Exclude lines that dont have an fmf_category
		Not robust to interference with df_template.csv
	'''
	#for some reason pandas loads eg NA and empty as nan. easiest comparison is with str
	return inptdf[inptdf.fmf_category.astype(str) != 'nan']

def pandas_2fmfHeader(df):
	'''
	Take the pandas input data_frame and write fmf header.

	Example:
	>>> df 
	key      | value | units | fmf_name    | fmf_category
	'sample' |'PbI3' |  ''      'Sample'   |'*reference'
	's_shot' |'False'|  ''   | 'Hi Res'    | 'paramaters'
	'n_avg'  | '16'  |  ''   |  'Averaging'| 'paramaters'
	'''
	fmf_cats = ['*reference', 'setup', 'parameters', '*data definitions']

	#below write new column with format we want for writing header
	df = filterDf(df).fillna('') #remove categories not relevant to metadata, remove nans
	df['formated'] = df['formated'] = df.fmf_name + ": " + df.value.map(str) + '' + df.units

	header = '; -*- coding: utf-8; fmf-version: 1.0 -*-\n'
	for cat in fmf_cats:
		header+='\n['+cat+']\n'
		s= df[df.fmf_category == cat].formated #mask (series)
		if not len(s) ==0:
			sub_cat= s.to_string(header = False, index = False)
		#strip white spaces at start of lines from pandas justify
			for line in sub_cat.split('\n'):
				header+=line.strip()+'\n'
				
	return header + '\n[*Data]'


def generate_file_name(df, _dir = 0):
	''' Generate a file name without overwriting'''
	_dict = df.value
	fname = _dict['date'].split(' ')[0]+'-'+_dict['user']+'-'+_dict['exp_name']+'-'+_dict['setup']
	if not _dir: _dir = _dict['sav_loc']

	overwrite, i = True, 0
	while overwrite:
		path = os.path.join(_dir, fname)
		i+=1
		overwrite = os.path.exists(path+'_%i.fmf'%i)
	return path+'_%i.fmf'%i

def save_to_file(inptMgerDf, x, y):
	''' Actually do the saving thing'''

	hdr = pandas_2fmfHeader(inptMgerDf)
	data = np.column_stack((x,y))
	format = ['%.6g']*data.shape[1]#number of columns

	#save to user location
	f = generate_file_name(inptMgerDf)
	np.savetxt(f,data, delimiter = '\t', fmt = format, header = hdr, comments = '')
	#print ('Data has been saved : ', f)
	return f
	
def append_save_to_file(f, x, y):
	''' Append new data point to save file'''
	#try:
	data = np.column_stack((x,y))
	format = ['%.6g']*data.shape[1]#number of columns
	with open(f, 'ab') as f_handle:
		np.savetxt(f_handle, data, delimiter = '\t', fmt=format)
	#except:
		#print ('Problem appending to file...')
	
		
def deposition_save_to_file(inptMgerDf, sampletime, QCM1_thickness, QCM1_rate, QCM2_thickness, QCM2_rate, QCM3_thickness, QCM3_rate, QCM4_thickness, QCM4_rate):
	''' Actually do the saving thing'''

	hdr = pandas_2fmfHeader(inptMgerDf)
	data = np.column_stack((sampletime, QCM1_thickness, QCM1_rate, QCM2_thickness, QCM2_rate, QCM3_thickness, QCM3_rate, QCM4_thickness, QCM4_rate))
	data = data.astype(float)
	format = ['%.3g']*data.shape[1]

	#save to user location
	f = generate_file_name(inptMgerDf)
	np.savetxt(f,data, delimiter = '\t', fmt = format, header = hdr, comments = '')
	#print ('Data has been saved : ', f)
	
	#save to group drive
	#try: 
		#y_address= '\\dc3.physics.ox.ac.uk\dfs\DAQ\CondensedMatterGroups\MRGroup\Transistor_data\\'
		#y_address+= inptMgerDf.loc['exp_name'].value + '\\' + inptMgerDf.loc['user'].value + '\\'
		#f = generate_file_name(inptMgerDf, y_address)
		#np.savetxt(f, data, delimiter = '\t', fmt = format, header = hdr, comments = '')
		#print ('Data has been saved remotely: ', f)
		
	#except:
		#print ('Data has not be saved remotely.')


def getWidgetValue(w):
	''' Get QWidget values w/o worry of its type'''
	if type(w) == QLineEdit:
		return str(w.text())
	elif type(w) == QSpinBox or type(w) == QDoubleSpinBox:
		return w.value()
	elif type(w) == QComboBox:
		return str(w.currentText())
	elif type(w) == QRadioButton or type(w) == QCheckBox:
		return bool(w.isChecked())	

	else:
		#print('oops: unexpected widget type %s at Utilities.getWidgetValue'%type(w))
		pass
	
def getWidgetUnits(w):
	''' Get QWidget values w/o worry of its type'''
	if type(w) == QComboBox:
		return 10**(-3*w.currentIndex())
		
	else:
		print('oops: unexpected widget type %s at Utilities.getWidgetValue'%type(w))
		

def setWidgetValue(w, v):
	'''set QWidget value w/o worry of its type.'''
	if type(w) == QLineEdit:
		w.setText('%s'%v)
	elif type(w) == QSpinBox or type(w) == QDoubleSpinBox:
		w.setValue(float(v))
	elif type(w) == QComboBox:
		index = w.findText(v, Qt.MatchFixedString)
		w.setCurrentIndex(index)	
	elif type(w) == QRadioButton or type(w) == QCheckBox:
		if v == 'False': w.setChecked(False)
		if v == 'True': w.setChecked(True)
	
def setWidgetUnits(w, v):
	'''set QWidget units w/o worry of its type.'''
	if type(w) == QComboBox:
		w.setCurrentIndex(abs(math.log10(float(v))/3))
		

def testModule():
	'''test all functions - requires a correct df_template.csv'''

	rm = visa.ResourceManager()
	print('inst addresses (visa)', rm.list_resources())
	print('serial_ports()>>', serial_ports())
	s = 'TEKTRONIX,MSO'
	print('atempting auto-discovery of inst (IDN has %s)'%s)
	print('res location is %s'%inst_autoFind(s, rm))
	df = pd.DataFrame.from_csv('df_template.csv', header = 1)
	df.loc['date'].value = '06-07-2016 10:13 etc'
	df.loc['user'].value = 'ramirez'
	df.loc['meas'].value = 'TPV'
	df.loc['sav_loc'].value = 'H:/Data/TPV_raw/test'
	print('DATAFRAME values')
	print(pandas_2fmfHeader(df))
	save_to_file(df, [1,2], [0,1])

