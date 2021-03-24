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