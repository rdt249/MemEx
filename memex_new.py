# this script contains misc. functions to help with the memory experiment

baud = 1000000 # baud rate for SPI comms. >10MHz does not work very well

import os
import csv

def log(data, header, file = "data/log.csv"): # create or update log given a data row along with a header row
    if os.path.isfile(file) is False: # check if file exists
        with open(file, 'w') as csvfile: # open file in write mode
            filewriter = csv.writer(csvfile,quoting=csv.QUOTE_MINIMAL) # make csv writer
            filewriter.writerow(header) # write column labels
    with open(file,'a') as csvfile: # open file in append mode
        filewriter = csv.writer(csvfile,quoting=csv.QUOTE_MINIMAL) # make csv writer
        filewriter.writerow(data) # write data

############################## GPIO ###################################

import busio, board
import digitalio as dio

cs_pins = [board.D5,board.D6,board.D13,board.D19,board.D26,board.D24,
           board.D25,board.D7,board.D12,board.D16,board.D20,board.D21]
cs = [None] * len(cs_pins)
for i in range(len(cs_pins)) :
    cs[i] = dio.DigitalInOut(cs_pins[i])
    cs[i].direction = dio.Direction.OUTPUT
    cs[i].value = True
    
#global spi
spi = busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO)
spi.try_lock()
spi.configure(baudrate=baud)
spi.unlock()

oe = dio.DigitalInOut(board.D23)
oe.direction = dio.Direction.OUTPUT
oe.value = True
        
############################# VOLTAGE-SETTING ##############################
        
import adafruit_mcp4728
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import busio
import board
import digitalio as dio
import time

i2c = busio.I2C(board.SCL, board.SDA)
dac = adafruit_mcp4728.MCP4728(i2c)
adc1 = AnalogIn(ADS.ADS1115(i2c), ADS.P0)
adc2 = AnalogIn(ADS.ADS1115(i2c), ADS.P1)
adc3 = AnalogIn(ADS.ADS1115(i2c), ADS.P2)
adc4 = AnalogIn(ADS.ADS1115(i2c), ADS.P3)

def comms_off() :
    #spi.deinit()
    #del spi
    #print(spi)
    for pin in cs :
        pin.value = False

def comms_on() :
    #global spi
    #spi = busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO)
    #spi.try_lock()
    #spi.configure(baudrate=baud)
    #spi.unlock()
    for pin in cs :
        pin.value = True

def set_out1(v) :
    y = int(1000 * v)
    dac.channel_a.raw_value = y
    error = int(1000 * (adc1.voltage - v))
    while error > 1 :
        #print('v',v,'y',y,'adc',adc1.voltage,'error',error)
        y = y - error
        dac.channel_a.raw_value = y
        error = int(1000 * (adc1.voltage - v))
        
def set_out2(v) :
    y = int(1000 * v)
    dac.channel_b.raw_value = y
    error = int(1000 * (adc2.voltage - v))
    while error > 1 :
        #print('v',v,'y',y,'adc',adc2.voltage,'error',error)
        y = y - error
        dac.channel_b.raw_value = y
        error = int(1000 * (adc2.voltage - v))

def set_out3(v) :
    y = int(1000 * v)
    dac.channel_c.raw_value = y
    error = int(1000 * (adc3.voltage - v))
    while error > 1 :
        #print('v',v,'y',y,'adc',adc3.voltage,'error',error)
        y = y - error
        dac.channel_c.raw_value = y
        error = int(1000 * (adc3.voltage - v))

def set_out4(v) :
    y = int(1000 * v)
    dac.channel_d.raw_value = y
    error = int(1000 * (adc4.voltage - v))
    while error > 1 :
        #print('v',v,'y',y,'adc',adc4.voltage,'error',error)
        y = y - error
        dac.channel_d.raw_value = y
        error = int(1000 * (adc4.voltage - v))

def set_outs(v1,v2,v3,v4) :
    comms_off()
    set_out1(v1)
    set_out2(v2)
    set_out3(v3)
    set_out4(v4)
    return adc1.voltage, adc2.voltage, adc3.voltage, adc4.voltage

def read_outs() :
    v1,v2,v3,v4 = adc1.voltage, adc2.voltage, adc3.voltage, adc4.voltage
    v1,v2,v3,v4 = round(v1,3),round(v2,3),round(v3,3),round(v4,3)
    return v1,v2,v3,v4

# initial nominal voltage levels. you can edit these but watch out for low-power DUTs
vnom_a = 3.3
vnom_b = 3.3
vnom_c = 3.3
vnom_d = 1.8
def set_nominal(va=None,vb=None,vc=None,vd=None) : # sets outs to nominal voltage, optional arguments set the nominal voltage
    # note that vdd will be set to 0 until a nominal value is defined
    if va is not None :
        global vnom_a
        vnom_a = va
    if vb is not None :
        global vnom_b
        vnom_b = vb
    if vc is not None :
        global vnom_c
        vnom_c = vc
    if vd is not None :
        global vnom_d
        vnom_d = vd
    set_outs(vnom_a,vnom_b,vnom_c,vnom_d)
    comms_on()
    v1,v2,v3,v4 = adc1.voltage, adc2.voltage, adc3.voltage, adc4.voltage
    v1,v2,v3,v4 = round(v1,3),round(v2,3),round(v3,3),round(v4,3)
    return v1,v2,v3,v4
    
########################### MACRO FUNCTIONS ###########################
    
def cycle() :
    set_outs(0,0,0,0)
    time.sleep(1)
    set_nominal()

def hold(v,t) :
    set_outs(v,v,v,v)
    time.sleep(t)
    set_nominal()
    
def wait(v) :
    set_outs(v,v,v,v)
    input('Holding at ' + str(v) + 'V... Press ENTER to continue.')
    set_nominal()
    
########################## MEMORY ACCESS ##############################
        
def fill(pin,data,size=32,addr_bytes=2) :
    set_nominal()
    
    # set mode to sequential
    mosi = [0x01,0x41]
    miso = [0] * len(mosi)
    cs[pin].value = False
    spi.write_readinto(buffer_out=mosi,buffer_in=miso)
    cs[pin].value = True

    # write data
    for s in range(size) :
        address = 1024 * s
        if addr_bytes == 2 :
            mosi = [0x02,(address>>8)&0xff,address&0xff] + [data] * 1024
        elif addr_bytes == 3:
            mosi = [0x02,(address>>16)&0xff,(address>>8)&0xff,address&0xff] + [data] * 1024
        miso = [0] * len(mosi)
        cs[pin].value = False
        spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        cs[pin].value = True
            
def read(pin,size=32,addr_bytes=2) :
    set_nominal()
    
    # set mode to sequential
    mosi = [0x01,0x41]
    miso = [0] * len(mosi)
    cs[pin].value = False
    spi.write_readinto(buffer_out=mosi,buffer_in=miso)
    cs[pin].value = True

    # read data
    data = []
    for s in range(size) :
        address = 1024 * s
        if addr_bytes == 2 :
            mosi = [0x03,(address>>8)&0xff,address&0xff] + [0xff] * 1024
        elif addr_bytes == 3:
            mosi = [0x03,(address>>16)&0xff,(address>>8)&0xff,address&0xff] + [0xff] * 1024
        miso = [0] * len(mosi)
        cs[pin].value = False
        spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        cs[pin].value = True
        if addr_bytes == 2:
            data += miso[3:]
        elif addr_bytes == 3:
            data += miso[4:]
    return data

############################# DUT-CHECKING ################################

#slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
#awake = [False] * len(slots)
#addr_bytes = [0] * len(slots)

def rollcall(status=0x41,show=True) :
    set_nominal()
    slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
    awake = [False] * len(slots)
    addr_bytes = [0] * len(slots)
    for i in range(len(slots)) :
        cs[i].value = True
        time.sleep(0.01)
        mosi = [0x01,status] # format mosi (write status register)
        miso = [0] * len(mosi) # pre-allocate miso
        cs[i].value = False
        spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        cs[i].value = True
        time.sleep(0.01)
        mosi = [0x05,0xff] # format mosi (read status register)
        miso = [0] * len(mosi) # pre-allocate miso
        cs[i].value = False
        spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        cs[i].value = True
        status = miso[1]

        if show :
            print(slots[i] + ':',end='\t')
            print('status=' + str(status),end='\t')
            if status >> 6 is 0:
                print('mode=byte',end='\t')
            elif status >> 6 is 1:
                print('mode=sequential',end='\t')
            elif status >> 6 is 2:
                print('mode=page',end='\t')
            else :
                print('mode=unknown',end='\t')

            if (status & 0x01) is True:
                print('hold=enabled',end='\t')
            else:
                print('hold=disabled',end='\t')

        mosi = [0x02,0x00,0x00,0x55] # format mosi (write 0x55 to address 0)
        miso = [0] * len(mosi) # pre-allocate miso
        cs[i].value = False
        spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        cs[i].value = True
        mosi = [0x03,0x00,0x00,0xff] # format mosi (read address 0)
        miso = [0] * len(mosi) # pre-allocate miso
        cs[i].value = False
        spi.write_readinto(buffer_out=mosi,buffer_in=miso)
        cs[i].value = True
        if miso[3] == 0x55 :
            if show :
                print('r/w=pass','addr=16bit',sep='\t')
            addr_bytes[i] = 2
            awake[i] = True
        else :
            mosi = [0x02,0x00,0x00,0x00,0x55] # format mosi (write 0x55 to address 0)
            miso = [0] * len(mosi) # pre-allocate miso
            cs[i].value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs[i].value = True
            mosi = [0x03,0x00,0x00,0x00,0xff] # format mosi (read address 0)
            miso = [0] * len(mosi) # pre-allocate miso
            cs[i].value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs[i].value = True
            if miso[4] == 0x55 :
                if show :
                    print('r/w=pass','addr=24bit',sep='\t')
                addr_bytes[i] = 3
                awake[i] = True
            else :
                if show :
                    print('r/w=fail','addr=unknown',sep='\t')
                addr_bytes[i] = 3
                awake[i] = False
    slots = [x for (x, y) in zip(slots, awake) if y]
    return slots,awake,addr_bytes

########################## LATCHUP MITIGATION ###################################

import adafruit_ina219, adafruit_mcp4728
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import busio, board

i2c = busio.I2C(board.SCL, board.SDA)
dac = adafruit_mcp4728.MCP4728(i2c)
pm1 = adafruit_ina219.INA219(i2c,addr=0x40)
pm2 = adafruit_ina219.INA219(i2c,addr=0x41)
pm3 = adafruit_ina219.INA219(i2c,addr=0x44)
pm4 = adafruit_ina219.INA219(i2c,addr=0x45)

def read_currents(show=True) :
    i1,i2,i3,i4 = pm1.current,pm2.current,pm3.current,pm4.current
    i1,i2,i3,i4 = round(i1,3),round(i2,3),round(i3,3),round(i4,3)
    return i1,i2,i3,i4

def latchdog(l1=1200,l2=1200,l3=1200,l4=1200):
    while True:
        [i1,i2,i3,i4] = [pm1.current,pm2.current,pm3.current,pm4.current]
        print(round(i1,3),round(i2,3),round(i3,3),round(i4,3),sep='\t')
        if abs(i1) > abs(l1) :
            print('Current spike detected by PM1. Cutting off channel power...')
            comms_off()
            v1 = adc1.voltage
            v2 = adc2.voltage
            v3 = adc3.voltage
            v4 = adc4.voltage
            dac.channel_a.raw_value = 0
            input('Power cut off, press ENTER to run headcount.')
            comms_on()
            headcount()
            input('Press ENTER to restore bias conditions and keep monitoring.')
            set_outs(v1,v2,v3,v4)

################################ FINDING VDR #####################################

import board, time
import digitalio as dio
import pandas as pd
import numpy as np

def bytes2bits(data) :
    result = []
    for i in range(len(data)) :
        result += [(data[i] >> b) & 1 for b in range(8)][::-1]
    return result

def test_retention(v,show=True,n=1,size=1):
    size = 1 # size in kB
    
    if v > 1.8 :
        print('about to test v > 1.8V ~~ this could damage low power chips.')
        cmd = input('enter "C" to continue')
        if cmd != 'C' :
            return 0
        
    pins = [1,2,3,4,5,6,7,8,9,10,11,12]
    slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
    #set_nominal(va=3.3,vb=3.3,vc=3.3,vd=1.8) # may need editing
    set_nominal()
    
    active,awake,addr_bytes = rollcall(show=False) 
    pins = [x for (x, y) in zip(pins, awake) if y]
    slots = [x for (x, y) in zip(slots, awake) if y]
    if show :
        print(v,*slots,sep='\t')
        
    flips = [[0] * (8192 * size)] * len(pins)
    total_flips = [0] * len(pins)
    while n > 0 :
        comms_on()
        for i in range(len(pins)) :
            fill(pins[i],0,size=size,addr_bytes=addr_bytes[i])
        set_outs(v,v,v,v) # may need editing
        time.sleep(1)
        set_nominal() # may need editing
        for i in range(len(pins)) :
            data = bytes2bits(read(pins[i],size=size,addr_bytes=addr_bytes[i]))
            flips[i] = [x + y for x,y in zip(flips[i],data)]
            fill(pins[i],255,size=size,addr_bytes=addr_bytes[i])
        set_outs(v,v,v,v) # may need editing
        time.sleep(1)
        set_nominal() # may need editing
        for i in range(len(pins)) : # for each memory
            data = bytes2bits(read(pins[i],size=size,addr_bytes=addr_bytes[i]))
            flips[i] = [x + (1-y) for x,y in zip(flips[i],data)]
            flips[i] = [x > 0 for x in flips[i]]
            total_flips[i] = sum(flips[i])
        if show :
            print('',*total_flips,sep='\t')
        n -= 1
    time.sleep(0.1)
    return flips

def find_vdr(n=5,inc=0.001,vmax=0.5,vmin='auto') :
    if vmin == 'auto' :
        vmin = 0
        auto = True
    else :
        auto = False
    v_range = np.arange(vmin,vmax+inc,inc)[::-1] # set voltage range
    active,awake,addr_bytes = rollcall(show=False)
    vdr = pd.DataFrame([[0] * len(active)] * 8192,columns = active)
    loss = pd.DataFrame(columns = ['V'] + active)
    print(*loss.columns,sep='\t')
    for v in v_range : # for every voltage level
        v = round(v,3)
        try :
            data = test_retention(v,n=n,show=False) # test data retention at voltage level (n times)
        except AttributeError :
            print('error (unable to set voltage) - returning early')
            break
        print(v,end='\t') # print voltage
        percent = [0] * len(data)
        for i in range(len(data)) : # for each memory
            percent[i] = sum(data[i])/8192
            print(percent[i],end='\t') # print total flips
            vdr[active[i]] = vdr[active[i]].mask(data[i],other=v).mask(vdr[active[i]]>0,other=vdr[active[i]])
        print()
        #try :
        loss.loc[len(loss.index)] = [v] + percent
        #except :
        #    print('error (DUT(s) stopped responding) - returning early')
        #    break
        if auto :
            if all([x==1.0 for x in percent]) :
                break
    loss = loss.set_index('V')
    loss.to_csv('data/sram/vdr/loss.csv')
    vdr.to_csv('data/sram/vdr/vdr.csv')
    return vdr,loss

############################ SEU DETECTION ############################

def auto_sweep(v_sweep=[3.3,0.6,0.3],seu_min=1000,inc=60,pattern=85,folder='data/sram/seu/test/') :
    size = 32 # size in kB
    active,awake = rollcall()
    pins = [board.D5,board.D6,board.D13,board.D19,board.D26,board.D24,
            board.D25,board.D7,board.D12,board.D16,board.D20,board.D21]
    pins = [x for (x, y) in zip(pins, awake) if y]
    slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
    slots = [x for (x, y) in zip(slots, awake) if y]
    #print(pins,slots)
    addr = []
    flips = []
    meta = []
    print()
    v_range = list(np.arange(v_sweep[0],v_sweep[1],v_sweep[2]))
    v_range = [round(x,3) for x in v_range]
    print('sweeping v_range =',v_range)
    print('seu minimum =',seu_min,'counts')
    print()
    print('V',*slots,sep='\t')
    for v in v_range :
        seu_total = [0] * len(slots)
        while any([x < seu_min for x in seu_total]) : # while any seu_total < seu_limit
            set_outs(3.3,3.3,3.3,1.8)
            comms_on()
            m = [0] * len(slots)
            for i in range(len(slots)) :
                m[i] = sram(cs=pins[i],name=slots[i],size=size)
                m[i].fill(pattern)
            comms_off()
            set_outs(v,v,v,v)
            set_outs(v,v,v,v)
            #read_outs()
            start = time.time()
            while time.time() - start < inc :
                ### latchup detection here
                pass
            set_outs(3.3,3.3,3.3,1.8)
            #read_outs()
            comms_on()
            data = pd.DataFrame(columns=slots)
            bits = [0] * len(slots)
            check = bytes2bits([pattern] * (1024 * size))
            for i in range(len(slots)) :
                data[slots[i]] = bytes2bits(m[i].export())
                data[slots[i]] = [x!=y for x,y in zip(data[slots[i]],check)]
                bits[i] = list(data[slots[i]].where(data[slots[i]]==True).dropna().index)
                seu_total[i] += data[slots[i]].sum()
            addr += [bits]
            pd.DataFrame(addr,columns=slots).to_csv(folder + 'addr.csv',index=False)
            print(v,*data.sum().values,sep='\t')
            flips += [list(data.sum())]
            pd.DataFrame(flips,columns=slots).to_csv(folder + 'flips.csv',index=False)
            meta += [[int(time.time()),inc,pattern,v,data.sum().sum(),size]]
            pd.DataFrame(meta,columns=['Timestamp(s)','Increment(s)','Pattern(byte)','Bias(v)','SEUs(#)',
                                       'Size(kB)']).to_csv(folder + 'meta.csv',index=False)
    print()
    print('end of sweep. outputs saved in',folder)
    print()

####################################### SYSTEM MONITORING ###########################################
        
import psutil,time
from gpiozero import CPUTemperature

def system() :
    cpu = CPUTemperature()
    print('Timestamp(s)','CPU(C)','CPU(MHz)''CPU(%)','Disk(%)',sep='\t')
    while True :
        print(int(time.time()),cpu.temperature,psutil.cpu_freq()[0],psutil.cpu_percent(),
              psutil.disk_usage('/')[3],sep='\t')
        time.sleep(1)

    