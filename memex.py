# this script contains misc. functions to help with the memory experiment

import os
import csv

def log(data, header, file = "data/log.csv"): # create or update log given a data row along with a header row
    if ~os.path.isfile(file): # check if file exists
        with open(file, 'w') as csvfile: # open file in write mode
            filewriter = csv.writer(csvfile,quoting=csv.QUOTE_MINIMAL) # make csv writer
            filewriter.writerow(header) # write column labels
    with open(file,'a') as csvfile: # open file in append mode
        filewriter = csv.writer(csvfile,quoting=csv.QUOTE_MINIMAL) # make csv writer
        filewriter.writerow(data) # write data

import time
import board
import busio
import adafruit_ina260
import adafruit_sht31d
import adafruit_mcp9808

def sense(): # print output of i2c sensors
    i2c = busio.I2C(board.SCL, board.SDA) # init i2c bus
    therm = adafruit_mcp9808.MCP9808(i2c) # init thermometer (mcp9808)
    hygro = adafruit_sht31d.SHT31D(i2c) # init hygrometer (sht31d)
    main = adafruit_ina260.INA260(i2c, address=0x40) # init power meter (ina260) for main power
    sd = adafruit_ina260.INA260(i2c, address=0x41) # init power meter (ina260) for sd power
    header = ["ThermTemp(C)", # set column titles (to print)
              "HygroTemp(C)",
              "RelativeHumidity(%)",
              "MainCurrent(mA)",
              "MainVoltage(V)",
              "MainPower(mW)",
              "SDCurrent(mA)",
              "SDVoltage(V)",
              "SDPower(mA)"]
    data = [therm.temperature, # get sensor data
            hygro.temperature,
            hygro.relative_humidity,
            main.current,
            main.voltage,
            main.power,
            sd.current,
            sd.voltage,
            sd.power]
    print(*header,sep='\t') # print column titles
    print(*data,sep='\t') # print data
    return data # return sensor data
        
import spidev
import time

# sd card commands
CMD0 = 0x40 # go to idle state (reset) - r1
ACMD41 = 0x41 # initialize (must be preceeded by CMD55) - r1
CMD8 = 0x48 # check operating conditions - r7
CMD9 = 0x49 # read CSD register
CMD10 = 0x4a # read CID register
CMD12 = 0x4c # stop transmission to read data
CMD16 = 0x50 # change block size
CMD17 = 0x51 # read a block
CMD18 = 0x52 # read multiple blocks
ACMD23 = 0x57 # set number of blocks to pre-erase with next multi-block write
CMD24 = 0x58 # write a block
CMD25 = 0x59 # write multiple blocks
CMD55 = 0x77 # application-specific command key (must be used before ACMDx)
CMD58 = 0x7a # read OCR (operational conditions register) - r3
DUMMY = 0xff

class sd_card(object):
    ''' 
    http://elm-chan.org/docs/mmc/mmc_e.html
    
    Anatomy of an SD card command:
    Byte:|  1  |  2   |  3   |  4   |  5   |  6   |  7   |  8
    MOSI:| CMD | data | data | data | data | crc  | 0xff | 
    MISO:|     |      |      |      |      |      |      | data
    
    Theoretical max SPI rate: 125 MHz
    Practical max SPI rate: 10 MHz?
    '''
    
    def __init__(self, spi, bus = 0, cs = 0, name = "SD", spi_hz = 1000000,timeout = 1,debug = False): # initialize sd card object
        start = time.time()
        
        # configuration (set by user)
        self.spi = spi # set up spi comms
        self.bus = bus # set spi bus (usually 0)
        self.cs = cs # set chip select pin
        self.name = name # set name tag
        self.spi_hz = spi_hz # set max spi rate
        self.debug = debug
        
        # parameters (set by program)
        self.block_size = None
        self.version = None
        self.voltage = None
        self.allow_1v8 = None
        self.uhs_status = None
        self.ccs = None
        self.ready = None
        
        # step 1: send 10 dummy bytes
        self.dummy(n=10) # send 10 dummy bytes
        
        # step 2: attempt reset
        time.sleep(0.1)
        response = -1
        while response is not 1:
            response = self.command(CMD0,crc = 0x97) # reset
            if time.time() - start > timeout:
                print("Error in memex.sd_card.__init__(): reset timed out")
                break
        
        # step 3: read ocr
        time.sleep(0.1)
        self.command(CMD58)
        
        # step 4: find sd version
        time.sleep(0.1)
        if self.command(CMD8, data = 0x1aa, crc = 0x86) == 1:
            self.version = 2
        else:
            print("Error in memex.sd_card.__init__(): unsupported sd version")
        
        # step 4: attempt init
        time.sleep(0.1)
        while response is not 0:
            self.command(CMD55)
            response = self.command(ACMD41,data = 0x40000000)
            if time.time() - start > timeout:
                print("Error in memex.sd_card.__init__(): init timed out")
                break
                
        # step 5: read ocr again
        time.sleep(0.1)
        self.command(CMD58)
        
    def command(self,cmd,data=0,crc=0xff,leave_open=False,timeout=1): # send a command with optional data, crc, and dummy
        start = time.time() # start timer
        tx = [cmd, (data>>24)&0xff, (data>>16)&0xff, (data>>8)&0xff, data&0xff, crc] # format message
        if self.debug:
            print("tx:",tx,end = "\t|\t") # for debug purposes
        if cmd in [CMD0,ACMD41,CMD9,CMD10,CMD16,CMD17,CMD18,ACMD23,CMD24,CMD25,CMD55]: # r1 style response
            rx_bytes = 1
        elif cmd in [CMD58,CMD8]: # r3 style response (or r7)
            rx_bytes = 5
        self.spi.open(self.bus,self.cs) # open spi comms
        self.spi.max_speed_hz = self.spi_hz # set max spi hz
        self.spi.writebytes(tx) # send command
        '''
        response = self.spi.readbytes(1)[0]
        while response is 0xff:
            print(hex(response))
            reponse = self.spi.readbytes(1)[0]
            if time.time() - start > timeout:
                print("Error in memex.sd_card.command(): timed out")
                return -1
        rx = [response] + self.spi.readbytes(rx_bytes - 1) # read response
        '''
        rx = self.spi.readbytes(rx_bytes) # read response
        if leave_open is False:
            self.spi.close() # close spi comms
        if self.debug:
            print("rx:",rx) # for debug purposes
        self.parse(rx,cmd) # parse response based on command
        return rx[0]
    
    def parse(self,data,cmd): # parse response based on command
        if cmd in [CMD0,ACMD41,CMD9,CMD10,CMD16,CMD17,CMD18,ACMD23,CMD24,CMD25,CMD55,CMD8]: # r1 style response (or r7)
            self.idle = data[0] & 0x01
            self.erase_reset = (data[0] & 0x02) >> 1
            self.illegal_command = (data[0] & 0x04) >> 2
            self.crc_error = (data[0] & 0x08) >> 3
            self.erase_error = (data[0] & 0x10) >> 4
            self.address_error = (data[0] & 0x20) >> 5
            self.parameter_error = (data[0] & 0x40) >> 6
            return data[0]
        elif cmd in [CMD58]: # r3 style response
            self.idle = data[0] & 0x01
            self.erase_reset = (data[0] & 0x02) >> 1
            self.illegal_command = (data[0] & 0x04) >> 2
            self.crc_error = (data[0] & 0x08) >> 3
            self.erase_error = (data[0] & 0x10) >> 4
            self.address_error = (data[0] & 0x20) >> 5
            self.parameter_error = (data[0] & 0x40) >> 6
            if data[3] == 0x80:
                self.voltage = 2.75
            elif data[2] == 0x01:
                self.voltage = 2.85
            elif data[2] == 0x02:
                self.voltage = 2.95
            elif data[2] == 0x04:
                self.voltage = 3.05
            elif data[2] == 0x08:
                self.voltage = 3.15
            elif data[2] == 0x10:
                self.voltage = 3.25
            elif data[2] == 0x20:
                self.voltage = 3.35
            elif data[2] == 0x40:
                self.voltage = 3.45
            elif data[2] == 0x80:
                self.voltage = 3.55
            self.allow_1v8 = data[1] & 0x01
            self.uhs_status = (data[1] & 0x20) >> 5
            self.ccs = (data[1] & 0x40) >> 6
            self.ready = (data[1] & 0x80) >> 7
            return data[0]
        else:
            print("Error in memex.sd_card.parse(): unknown reponse format")
            return -1
    
    def dummy(self,n = 1): # send n dummy bytes
        self.spi.open(self.bus,self.cs) # open spi comms
        self.spi.max_speed_hz = self.spi_hz # set max spi hz
        while n > 0:
            self.spi.writebytes([DUMMY]) # send dummy byte
            n -= 1
        self.spi.close() # close spi comms
        
    def set_block_size(self,size):
        self.command(CMD16,size)
        self.block_size = size
        return self.block_size
    
    def read_block(self,address,timeout = 10): # read starting at specified byte
        start = time.time()
        if self.block_size is None:
            print("Error in memex.sd_card.read_block(): block size not set")
            return -1
        response = self.command(CMD17,data=address,leave_open=True)
        i = 0
        while response is not [0xfe]:
            print(i,hex(response))
            i += 1
            response = self.spi.readbytes(1)[0]
            if time.time() - start > timeout:
                print("Error in memex.sd_card.read_block(): timed out")
                return -1
            if response < 0x20:
                print("Error in memex.sd_card.read_block(): data error, code",hex(response))
                return -1
        data = self.spi.readbytes(self.block_size)
        self.spi.close()
        return data
    
    def write_block(self,address,data,timeout=10): # write data starting at specified byte
        start = time.time()
        if len(data) is not self.block_size:
            print("Error in memex.sd_card.write_block(): data does not fit block size")
            return -1
        response = self.command(CMD24,data=address,leave_open=True)
        if response is not 0:
            print("Error in memex.sd_card.write_block(): bad response")
            return -1
        time.sleep(0.1)
        self.spi.writebytes([DUMMY] + data + [DUMMY,DUMMY]) # send data prefixed by a dummy and suffixed by 2 dummies
        response = self.spi.readbytes(1)[0] & 0x1f
        self.spi.close()
        if response is 0x05:
            pass # data accepted
        elif response is 0x0b:
            print("Error in memex.sd_card.write_block(): crc error")
            return -1
        elif response is 0x0d:
            print("Error in memex.sd_card.write_block(): write error")
            return -1
        return response
    
    def print_status(self): # print operating conditions register
        response = self.command(0x7a) # update object parameters
        if response is 0xff: # check response
            print("Error in memex.sd_card.print_status(): no response")
            return -1
        # print r1
        print("r1:\tidle:",self.idle)
        print("\terase_reset:",self.erase_reset)
        print("\tillegal_command:",self.illegal_command)
        print("\tcrc_error:",self.crc_error)
        print("\taddress_error:",self.address_error)
        print("\tparameter_error:",self.parameter_error)
        # print ocr
        print("ocr:\tvoltage:",self.voltage)
        print("\tallow_1v8:",self.allow_1v8)
        print("\tuhs_status:",self.uhs_status)
        print("\tccs:",self.ccs)
        print("\tready:",self.ready)
        # print config
        print("config:\tspi:",self.spi)
        print("\tbus:",self.bus)
        print("\tcs:",self.cs)
        print("\tname:",self.name)
        print("\tspi_hz:",self.spi_hz)
        print("\tdebug:",self.debug)
        return response
    
# sram dependencies
import board
from busio import SPI
from digitalio import DigitalInOut
from digitalio import Direction
from adafruit_bus_device.spi_device import SPIDevice
   
# memex.sram() object
class sram(object):
    '''
    based on Microchip 23LC1024 (1 Mbit) and 23K256 (256 kbit)
    https://ww1.microchip.com/downloads/en/DeviceDoc/20005142C.pdf
    '''
    def __init__(self,
                 spi = SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO),
                 cs = DigitalInOut(board.D8),
                 hz = 5000000,
                 size = 32,
                 name = "SRAM",
                 debug = False):

        self.spi = spi
        self.spi.try_lock()
        self.spi.configure(baudrate=hz)
        self.spi.unlock()
        
        self.cs = cs
        self.cs.direction = Direction.OUTPUT
        self.cs.value = True
        
        self.size = size
        self.name = name
        self.debug = debug
        self.mode = None
        self.hold = None
        time.sleep(0.1)
        self.read_status()
        
    def read_status(self): # read status register
        if self.debug:
            print("(read_status)",end=" ")
        mosi = [0x05,0xff] # format mosi
        miso = [0] * len(mosi) # pre-allocate miso
        if self.debug:
            print("MOSI:",mosi,end="\t|\t")
        self.cs.value = False
        self.spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        self.cs.value = True
        if self.debug:
            print("MISO:",miso)
        status = miso[1]
        # check response
        if status is 0xff:
            print("Error in memex.sram.read_status(): no response")
            return -1
        # check mode
        if status >> 6 is 0:
            self.mode = "byte"
        elif status >> 6 is 1:
            self.mode = "page"
        elif status >> 6 is 2:
            self.mode = "sequential"
        # check hold bit
        if (status & 0x01) is True:
            self.hold = True
        else:
            self.hold = False
        return status
    
    def set_status(self,mode="sequential",hold=False): # set status with "mode" and "hold"
        if self.debug:
            print("(set_status)",end=" ")
        # set mode
        if mode is "byte":
            status = 0
        elif mode is "page":
            status = 0x40
        elif mode is "sequential":
            status = 0x80
        # set hold
        if hold is False:
            status += 1
        mosi = [0x01,status]
        miso = [0] * len(mosi)
        if self.debug:
            print("MOSI:",mosi,end="\t|\t")
        self.cs.value = False
        self.spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        self.cs.value = True
        if self.debug:
            print("MISO:",miso)
        return 0
    
    def read(self,address,n=1): # read data starting at address. read multple bytes by defining "n"
        if self.debug:
            print("(read)",end=" ")
        # format message
        if self.size < 1024: # 16-bit address
            mosi = [0x03,(address>>8)&0xff,address&0xff] + ([0xff] * n)
        else: # 24-bit address
            mosi = [0x03,(address>>16)&0xff,(address>>8)&0xff,address&0xff] + ([0xff] * n)
        miso = [0] * len(mosi)
        # spi transfer
        if self.debug:
            print("MOSI:",mosi,end="\t|\t")
        self.cs.value = False
        self.spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        self.cs.value = True
        if self.debug:
            print("MISO:",miso)
        if self.size < 1024: # 16-bit address
            data = miso[3:]
        else: # 24-bit address
            data = miso[4:]
        return data
    
    def write(self,address,data,n=1): # write data starting at address. write multiple bytes by inputting a list or defining "n"
        if self.debug:
            print("(write)",end=" ")
        # format address
        if self.size < 1024: # 16-bit address
            mosi = [0x02,(address>>8)&0xff,address&0xff]
        else: # 24-bit address
            mosi = [0x02,(address>>16)&0xff,(address>>8)&0xff,address&0xff]
        # format data
        if type(data) is list:
            mosi += data * n
        else:
            mosi += [data] * n
        miso = [0] * len(mosi)
        if self.debug:
            print("MOSI:",mosi,end="\t|\t")
        # spi transfer
        self.cs.value = False
        self.spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        self.cs.value = True
        if self.debug:
            print("MISO:",miso)
        return 0
    
    def fill(self,data): # write data to every index of memory
        for block in range(self.size):
            self.write(1024*block,data,n=1024)
        return 0
    
    def check(self,data_pattern): # compare every index of memory to data_pattern, return tally of mismatched bits
        tally = 0
        for block in range(self.size):
            data = self.read(1024*block,n=1024) # read 1024 bytes starting at 1024*block
            for byte in range(1024): # iterate over block
                if data[byte] != data_pattern: # if data doesn't match
                    for bit in range(8): # check each bit in the byte
                        tally += ((data[byte] ^ data_pattern) >> bit) & 0x01
        return tally
    
    def save(self,file = "data/sram/save.csv"): # save sram state as a single-row csv with specified file path
        data = [] # init data as list
        for block in range(self.size):
            data += self.read(1024*block,n=1024) # read 1024 bytes starting at 1024*block
        with open(file, 'w') as csvfile: # open file in write mode
            filewriter = csv.writer(csvfile,quoting=csv.QUOTE_MINIMAL) # make csv writer
            filewriter.writerow(data) # write column labels
        return 0