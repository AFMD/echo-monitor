""" 
Driver for Inficon SQC310C QCM controller.
Code adapted from https://github.com/CINF/PyExpLabSys/blob/master/PyExpLabSys/drivers/inficon_sqm160.py
"""

import serial
import time

class inficon310C(object):
    """ Driver for Inficon SQM160 QCM controller """
    def __init__(self, port='/dev/ttyUSB0'):
        # This command opens the serial port
        self.serial = serial.Serial(port=port,
                                    baudrate=115200,
                                    timeout=2,
                                    bytesize=serial.EIGHTBITS,
                                    xonxoff=True)
        
        ### EXPLANATION OF SERIAL PARAMETERS
        #port – Device name or None.
        #baudrate (int) – Baud rate such as 9600 or 115200 etc.
        #bytesize – Number of data bits. Possible values: FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
        #parity – Enable parity checking. Possible values: PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, PARITY_SPACE
        #stopbits – Number of stop bits. Possible values: STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
        #timeout (float) – Set a read timeout value.
        #xonxoff (bool) – Enable software flow control.
        #rtscts (bool) – Enable hardware (RTS/CTS) flow control.
        #dsrdtr (bool) – Enable hardware (DSR/DTR) flow control.
        #write_timeout (float) – Set a write timeout value.
        #inter_byte_timeout (float) – Inter-character timeout, None to disable (default).
        #Raises:	
        #ValueError – Will be raised when parameter are out of range, e.g. baud rate, data bits.
        #SerialException – In case the device can not be found or can not be configured.        
       
        print (self.serial.name) # Check which port was really used

    def comm(self, command):
        """ Implements actual communication with device """
        length = chr(len(command) + 34)       
        crc = self.crc_calc(length + command)
        command = '!' + length + command + crc[0] + crc[1]
        command_bytes = bytearray()
        for i in range(0, len(command)):
            command_bytes.append(ord(command[i]))
        error = 0
        while (error > -1) and (error < 20):
            self.serial.write(command_bytes) # sends command to instrument in byte type
            time.sleep(0.1) # Give it a second (or a tenth of one)
            reply = self.serial.read(self.serial.inWaiting()) # Reads number of bytes in recieved input buffer
            reply_chr = reply.decode('cp437') # Convert to string as serial for python 3 reads back bytes (?) utf-8 fucks up.
            crc = self.crc_calc(reply_chr[1:-2]) # make crc error check?
            try:
                crc_ok = (reply[-2] == ord(crc[0]) and reply[-1] == ord(crc[1]))
            except IndexError:
                crc_ok = False
            if crc_ok:
                error = -1
                return_val = reply[3:-2]
                return return_val
            else:
                error = error + 1
        return 

    @staticmethod # This means the method can be called without an instance of the class
    def crc_calc(input_string):
        """ Calculate crc value of command """
        command_string = []
        for i in range(0, len(input_string)):
            command_string.append(ord(input_string[i])) # Input string is already in ordinal format. This is silly
        crc = int('3fff', 16) # Convert 3fff (hexidecimal) to an integer in base 16
        mask = int('2001', 16) # Convert 2001 (hexidecimal) to an integer in base 16
        for command in command_string:
            crc = command ^ crc
            for i in range(0, 8):
                old_crc = crc
                crc = crc >> 1 # Bitwise right shift 
                if old_crc % 2 == 1:
                    crc = crc ^ mask
        crc1_mask = int('1111111', 2)
        crc1 = chr((crc & crc1_mask) + 34)
        crc2 = chr((crc >> 7) + 34) 
        return(crc1, crc2)

    def show_version(self):
        """ Read the firmware version """
        command = '@'
        return self.comm(command)

    def film_name(self, film_num=1):
        """ Read the film name """
        command = 'A1 ' +str(film_num) +'?'
        value_string = self.comm(command)
        value_string = value_string.decode()
        return value_string
        

    def rate(self, channel=1):
        """ Return the deposition rate """
        command = 'L' + str(channel)
        value_string = self.comm(command)
        rate = float(value_string)
        return rate

    def thickness(self, channel=1):
        """ Return the film thickness """
        command = 'N' + str(channel)
        value_string = self.comm(command)
        value_string = value_string.decode()
        thickness = str(value_string)
        return thickness

    def frequency(self, channel=1):
        """ Return the frequency of the crystal """
        command = 'P' + str(channel)
        value_string = self.comm(command)
        frequency = float(value_string)
        return frequency

    def crystal_stats(self, channel=1):
        """ Read crystal stats: status, frequency, and crystal life of the requested sensor """
        command = 'PA' + str(channel)
        value_string_bytes = self.comm(command)
        value_string = value_string_bytes.decode()
        status, frequency, life = value_string.split(' ')
        #life = float(value_string)
        return status, frequency,life

if __name__ == "__main__":
    INFICON = inficon310C()
    
    # Test driver functionality
    print(INFICON.show_version())
    print('The rate (channel 1) is', INFICON.rate(1))
    print('The rate (channel 2) is', INFICON.rate(2))
    print('The thickness (channel 1) is', INFICON.thickness(1))
    print('The frequency (channel 1) is', INFICON.frequency(1))
    print('QCM 1 (status, frequency, lifetime):', INFICON.crystal_stats(1))
    print('The film name in slot 1 is', INFICON.film_name())