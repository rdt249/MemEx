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

def track(func,arg = None): # returns the elapsed time for the input function with an argument
    time_start = time.time() # record time before function starts
    func(arg) # execute function
    return time.time() - time.start # find elapsed time

import spidev
import time

class sd_card(object):
    ''' 
    https://openlabpro.com/guide/interfacing-microcontrollers-with-sd-card/
    http://rjhcoding.com/avrc-sd-interface-3.php
    
    Anatomy of an SD card command:
    
    Byte:|  1  |  2   |  3   |  4   |  5   |  6   |  7   |  8
    MOSI:| CMD | data | data | data | data | 0xff | 0xff | 
    MISO:|     |      |      |      |      |      |      | data
    
    Theoretical max SPI rate: 125 MHz
    Practical max SPI rate: 10 MHz?
    '''
    
    def __init__(self, spi, bus = 0, cs = 0, name = "SD", spi_hz = 10000000): # initialize sd card object
        self.spi = spi # set up spi comms
        self.bus = bus # set spi bus (usually 0)
        self.cs = cs # set chip select pin
        self.name = name # set name tag
        self.spi_hz = spi_hz # set max spi rate
        self.block_size = None
        
        self.spi.open(self.bus,self.cs) # open spi comms
        spi.max_speed_hz = self.spi_hz # set max spi hz
        self.spi.writebytes([0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff]) # send 10 dummy bytes
        self.spi.close() # close spi comms
        
        print("reset:",self.reset())
        print("version:",self.version())
        print("read_ocr:",self.read_ocr())
        print("init:",self.init())
                  
    def reset(self,timeout = 1): # reset sd card
        start = time.time() # record start time
        self.spi.open(self.bus,self.cs) # open spi comms
        self.spi.max_speed_hz = self.spi_hz # set max spi hz
        self.spi.writebytes([0x40,0x00,0x00,0x00,0x00,0x95,0xff]) # send command, data[4], crc, and dummy
        response = self.spi.readbytes(1)[0] # get response
        while response not in [1]: # check if response is acceptable
            response = self.spi.readbytes(1)[0] # get response
            if time.time() - start > timeout: # check timeout
                print("Error in memex.sd_card.reset(): timed out") # print error
                break # break out of while loop
        self.spi.close() # close spi comms
        return response
                  
    def version(self,timeout = 1): # check sd card version
        start = time.time() # record start time
        self.spi.open(self.bus,self.cs) # open spi comms
        self.spi.max_speed_hz = self.spi_hz # set max spi hz
        self.spi.writebytes([0x48,0x00,0x00,0x01,0xaa,0x87,0xff]) # send command, data[4], crc, and dummy
        response = self.spi.readbytes(1)[0] # get response
        while response not in [1,5]: # check if response is acceptable
            response = self.spi.readbytes(1)[0] # get response
            if time.time() - start > timeout: # check timeout
                print("Error in memex.sd_card.version(): timed out") # print error
                break # break out of while loop
        self.spi.close() # close spi comms
        return response
    
    def read_ocr(self): # read the operating conditions register (OCR)
        self.spi.open(self.bus,self.cs) # open spi comms
        self.spi.max_speed_hz = self.spi_hz # set max spi hz
        self.spi.writebytes([0x7a,0x00,0x00,0x00,0x00,0x75,0xff]) # send command, data[4], crc, and dummy
        response = self.spi.readbytes(5) # get response
        self.spi.close() # close spi comms
        return response
    
    def init(self,timeout = 1): # initialize sd card: repeat cmd55 then acmd41 until response is 0
        start = time.time() # record start time
        response = -1
        while response not in [0]:
            # CMD55
            self.spi.open(self.bus,self.cs) # open spi comms
            self.spi.max_speed_hz = self.spi_hz # set max spi hz
            self.spi.writebytes([0x55,0x00,0x00,0x00,0x00,0xff,0xff]) # send command, data[4], crc, and dummy
            response = self.spi.readbytes(1)[0] # get response
            self.spi.close() # close spi comms
            # ACMD41
            self.spi.open(self.bus,self.cs) # open spi comms
            self.spi.max_speed_hz = self.spi_hz # set max spi hz
            self.spi.writebytes([0x41,0x00,0x00,0x00,0x00,0xff,0xff]) # send command, data[4], crc, and dummy
            response = self.spi.readbytes(1)[0] # get response
            self.spi.close() # close spi comms
            # check timeout
            if time.time() - start > timeout:
                print("Error in memex.sd_card.init(): timed out")
                break
        return response
    
    def set_block_size(self,size,timeout = 1):
        start = time.time()
        self.block_size = size
        data = [(size>>24)&0xff, (size>>16)&0xff, (size>>8)&0xff, size&0xff]
        self.spi.open(self.bus,self.cs) # open spi comms
        self.spi.max_speed_hz = self.spi_hz # set max spi hz
        self.spi.writebytes([0x16] + data + [0xff,0xff]) # send command, data[4], crc, and dummy
        response = self.spi.readbytes(1)[0] # get response
        while response not in [0]: # check if response is acceptable
            response = self.spi.readbytes(1)[0] # get response
            if time.time() - start > timeout: # check timeout
                print("Error in memex.sd_card.block_size(): timed out") # print error
                break # break out of while loop
        self.spi.close() # close spi comms
        return response

    def read(self,address,timeout = 1):
        start = time.time()
        data = [(address>>24)&0xff, (address>>16)&0xff, (address>>8)&0xff, address&0xff]
        if self.block_size is None:
            print("Error in memex.sd_card.read(): block size not set")
            return -1
        self.spi.open(self.bus,self.cs) # open spi comms
        self.spi.max_speed_hz = self.spi_hz # set max spi hz
        self.spi.writebytes([0x17] + data + [0xff,0xff]) # send command, data[4], crc, and dummy
        
        response = self.spi.readbytes(1)[0] # get response
        while response not in [0]: # check if response is acceptable
            response = self.spi.readbytes(1)[0] # get response
            if time.time() - start > timeout: # check timeout
                print("Error in memex.sd_card.read(): timed out") # print error
                break # break out of while loop
                
        response = self.spi.readbytes(1)[0] # get response
        while response not in [254, 0xfe]: # check if response is acceptable
            response = self.spi.readbytes(1)[0] # get response
            if time.time() - start > timeout: # check timeout
                print("Error in memex.sd_card.read(): timed out") # print error
                break # break out of while loop
        
        data = self.spi.readbytes(self.block_size) # get block data
        self.spi.close() # close spi comms
        return data