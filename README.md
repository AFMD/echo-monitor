# ECHO Monitor
Code for monitoring and logging ECHO
Run from the command line:
> python main_program.py

## Version 2 updates:
- window resizing
- continuous saving on measurement
- (many) bug fixes

## Features
- Deposition monitoring (rates + thickness)
- Electrical measurements substrate

### Still to be added
- Substrate heating control
- Pressure logging
- Source temperature logging

## Easiest way to install 'command line instructions in quotations':
- download anaconda3
- pyqt4 'conda install qt=4'
- pyvisa 'conda install --channel https://conda.anaconda.org/conda-forge pyvisa'
- pyvisa-py 'pip install pyvisa-py'
- serial 'conda install pyserial'
- Required group on DAQ comp 'sudo usermod -a -G GroupName UserName'
