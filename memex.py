# this script contains misc. functions to help with the memory experiment

baud = 1000000 # baud rate for SPI comms. >10MHz does not work very well

trial = None

# initial nominal voltage levels. you can edit these but watch out for low-power DUTs
vnom_a = 3.3
vnom_b = 3.3
vnom_c = 3.3
vnom_d = 1.8

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

########################## MEMORY ACCESS ##############################
    
import digitalio as dio
    
def fill(pin,data,size=32,addr_bytes=2) :
    with busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO) as spi :
        spi.try_lock()
        spi.configure(baudrate=baud)
        spi.unlock()
        with dio.DigitalInOut(pin) as cs :
            cs.direction = dio.Direction.OUTPUT
            cs.value = True

            # set mode to sequential
            mosi = [0x01,0x41]
            miso = [0] * len(mosi)
            cs.value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs.value = True
            
            # set mode to sequential
            mosi = [0x01,0x41]
            miso = [0] * len(mosi)
            cs.value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs.value = True

            # write data
            for s in range(size) :
                address = 1024 * s
                if addr_bytes == 2 :
                    mosi = [0x02,(address>>8)&0xff,address&0xff] + [data] * 1024
                elif addr_bytes == 3:
                    mosi = [0x02,(address>>16)&0xff,(address>>8)&0xff,address&0xff] + [data] * 1024
                miso = [0] * len(mosi)
                cs.value = False
                spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                cs.value = True
        spi.deinit()
        
def fill_alt(pin,data,size=32,addr_bytes=2) :
    with busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO) as spi :
        spi.try_lock()
        spi.configure(baudrate=baud)
        spi.unlock()
        with dio.DigitalInOut(pin) as cs :
            cs.direction = dio.Direction.OUTPUT
            cs.value = True

            # set mode to sequential
            mosi = [0x01,0x41]
            miso = [0] * len(mosi)
            cs.value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs.value = True
            
            # set mode to sequential
            mosi = [0x01,0x41]
            miso = [0] * len(mosi)
            cs.value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs.value = True

            # write data
            for s in range(size) :
                address = 1024 * s
                for b in range(1024) :
                    addr = address + b
                    if addr_bytes == 2 :
                        mosi = [0x02,(addr>>8)&0xff,addr&0xff] + [data]
                    elif addr_bytes == 3:
                        mosi = [0x02,(addr>>16)&0xff,(addr>>8)&0xff,addr&0xff] + [data]
                    miso = [0] * len(mosi)
                    cs.value = False
                    spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                    cs.value = True
        spi.deinit()
            
def read(pin,size=32,addr_bytes=2) :
    with busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO) as spi :
        spi.try_lock()
        spi.configure(baudrate=baud)
        spi.unlock()

        with dio.DigitalInOut(pin) as cs :
            cs.direction = dio.Direction.OUTPUT
            cs.value = True

            # set mode to sequential
            mosi = [0x01,0x41]
            miso = [0] * len(mosi)
            cs.value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs.value = True
            
            # set mode to sequential
            mosi = [0x01,0x41]
            miso = [0] * len(mosi)
            cs.value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs.value = True

            # read data
            data = []
            for s in range(size) :
                address = 1024 * s
                if addr_bytes == 2 :
                    mosi = [0x03,(address>>8)&0xff,address&0xff] + [0xff] * 1024
                elif addr_bytes == 3:
                    mosi = [0x03,(address>>16)&0xff,(address>>8)&0xff,address&0xff] + [0xff] * 1024
                miso = [0] * len(mosi)
                cs.value = False
                spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                cs.value = True
                if addr_bytes == 2:
                    data += miso[3:]
                elif addr_bytes == 3:
                    data += miso[4:]
        spi.deinit()
    return data

def read_alt(pin,size=32,addr_bytes=2) :
    with busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO) as spi :
        spi.try_lock()
        spi.configure(baudrate=baud)
        spi.unlock()

        with dio.DigitalInOut(pin) as cs :
            cs.direction = dio.Direction.OUTPUT
            cs.value = True

            # set mode to sequential
            mosi = [0x01,0x41]
            miso = [0] * len(mosi)
            cs.value = False
            spi.write_readinto(buffer_out=mosi,buffer_in=miso)
            cs.value = True

            # read data
            data = []
            for s in range(size) :
                address = 1024 * s
                for b in range(1024) :
                    addr = address + b
                    if addr_bytes == 2 :
                        mosi = [0x03,(addr>>8)&0xff,addr&0xff] + [0xff]
                    elif addr_bytes == 3:
                        mosi = [0x03,(addr>>16)&0xff,(addr>>8)&0xff,addr&0xff] + [0xff]
                    miso = [0] * len(mosi)
                    cs.value = False
                    spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                    cs.value = True
                    if addr_bytes == 2:
                        data += miso[3:]
                    elif addr_bytes == 3:
                        data += miso[4:]
        spi.deinit()
    return data
        
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
    pin_list = [board.D5,board.D6,board.D13,board.D19,board.D26,board.D24,
                board.D25,board.D7,board.D12,board.D16,board.D20,board.D21,
                board.D23]
    for p in pin_list :
        with dio.DigitalInOut(p) as pin :
            pin.direction = dio.Direction.OUTPUT
            pin.value = False

def comms_on() :
    pin_list = [board.D5,board.D6,board.D13,board.D19,board.D26,board.D24,
                board.D25,board.D7,board.D12,board.D16,board.D20,board.D21,
                board.D23]
    for p in pin_list :
        with dio.DigitalInOut(p) as pin :
            pin.direction = dio.Direction.OUTPUT
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

############################# DUT-CHECKING ################################

global active,awake,addr_bytes
active = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
awake = [False] * len(active)
addr_bytes = [0] * len(active)

def rollcall(status=0x41,show=True) :
    set_nominal()
    pins = [board.D5,board.D6,board.D13,board.D19,board.D26,board.D24,
            board.D25,board.D7,board.D12,board.D16,board.D20,board.D21]
    slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
    global active, awake, addr_bytes
    #awake = [False] * len(pins)
    #addr_bytes = [0] * len(pins)
    with busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO) as spi :
        spi.try_lock()
        spi.configure(baudrate=baud)
        spi.unlock()
        for i in range(len(pins)) :
            with dio.DigitalInOut(pins[i]) as cs :
                cs.direction = dio.Direction.OUTPUT
                cs.value = True
                time.sleep(0.01)
                mosi = [0x01,status] # format mosi (write status register)
                miso = [0] * len(mosi) # pre-allocate miso
                cs.value = False
                spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                cs.value = True
                time.sleep(0.01)
                mosi = [0x05,0xff] # format mosi (read status register)
                miso = [0] * len(mosi) # pre-allocate miso
                cs.value = False
                spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                cs.value = True
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
                cs.value = False
                spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                cs.value = True
                mosi = [0x03,0x00,0x00,0xff] # format mosi (read address 0)
                miso = [0] * len(mosi) # pre-allocate miso
                cs.value = False
                spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                cs.value = True
                if miso[3] == 0x55 :
                    if show :
                        print('r/w=pass','addr=16bit',sep='\t')
                    addr_bytes[i] = 2
                    awake[i] = True
                else :
                    mosi = [0x02,0x00,0x00,0x00,0x55] # format mosi (write 0x55 to address 0)
                    miso = [0] * len(mosi) # pre-allocate miso
                    cs.value = False
                    spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                    cs.value = True
                    mosi = [0x03,0x00,0x00,0x00,0xff] # format mosi (read address 0)
                    miso = [0] * len(mosi) # pre-allocate miso
                    cs.value = False
                    spi.write_readinto(buffer_out=mosi,buffer_in=miso)
                    cs.value = True
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
        spi.deinit()
    slots = [x for (x, y) in zip(slots, awake) if y]
    active = slots
    return active,awake,addr_bytes

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

def test_retention(v,show=True,n=1,size=1,alt=False):
    size = 1 # size in kB
    
    if v > 1.8 :
        print('about to test v > 1.8V ~~ this could damage low power chips.')
        input('enter "C" to continue')
    
    pins = [board.D5,board.D6,board.D13,board.D19,board.D26,board.D24,
            board.D25,board.D7,board.D12,board.D16,board.D20,board.D21]
    slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
    set_nominal() # may need editing
    
    global active,awake,addr_bytes
    #active,awake,addr_bytes = rollcall(show=False) 
    slots = [x for (x, y) in zip(slots, awake) if y]
    pins = [x for (x, y) in zip(pins, awake) if y]
    addr = [x for (x, y) in zip(addr_bytes, awake) if y]
    if show :
        print(v,*slots,sep='\t')
        
    flips = [[0] * (8192 * size)] * len(pins)
    total_flips = [0] * len(pins)
    while n > 0 :
        comms_on()
        for i in range(len(pins)) :
            if alt :
                fill_alt(pins[i],0,size=size,addr_bytes=addr[i])
            else :
                fill(pins[i],0,size=size,addr_bytes=addr[i])
        set_outs(v,v,v,v) # may need editing
        time.sleep(1)
        set_nominal() # may need editing
        for i in range(len(pins)) :
            if alt :
                data = bytes2bits(read_alt(pins[i],size=size,addr_bytes=addr[i]))
                fill_alt(pins[i],255,size=size,addr_bytes=addr[i])
            else :
                data = bytes2bits(read(pins[i],size=size,addr_bytes=addr[i]))
                fill(pins[i],255,size=size,addr_bytes=addr[i])
            flips[i] = [x + y for x,y in zip(flips[i],data)]
        set_outs(v,v,v,v) # may need editing
        time.sleep(1)
        set_nominal() # may need editing
        for i in range(len(pins)) : # for each memory
            if alt :
                data = bytes2bits(read_alt(pins[i],size=size,addr_bytes=addr[i]))
            else :
                data = bytes2bits(read(pins[i],size=size,addr_bytes=addr[i]))
            flips[i] = [x + (1-y) for x,y in zip(flips[i],data)]
            flips[i] = [x > 0 for x in flips[i]]
            total_flips[i] = sum(flips[i])
        if show :
            print('',*total_flips,sep='\t')
        n -= 1
    time.sleep(0.1)
    return flips

def find_vdr(n=5,inc=0.001,vmax=0.5,vmin='auto',alt=False) :
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
            data = test_retention(v,n=n,show=False,alt=alt) # test data retention at voltage level (n times)
        except AttributeError :
            print('error (unable to set voltage) ~~ returning early')
            break
        except OSError :
            print('error (out of disk space) ~~ returning early')
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
    
def seu_trial(v='auto',t='auto',size=32,pattern=85,threshold=1000,alt=False) :
    if trial is None:
        print('please use memex.create_trial() to specify a trial csv')
        return 0
    print(trial)
        
    active,awake,addr_bytes = rollcall(show=False)
    pins = [board.D5,board.D6,board.D13,board.D19,board.D26,board.D24,
            board.D25,board.D7,board.D12,board.D16,board.D20,board.D21]
    pins = [x for (x, y) in zip(pins, awake) if y]
    slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
    slots = [x for (x, y) in zip(slots, awake) if y]
    addr = [x for (x, y) in zip(addr_bytes, awake) if y]
    try :
        flips = pd.read_csv(trial)
    except FileNotFoundError :
        flips = pd.DataFrame(columns=['v','t']+slots)
    
    for i in range(len(slots)) :
        if alt :
            fill_alt(pins[i],pattern,size=size,addr_bytes=addr[i])
        else :
            fill(pins[i],pattern,size=size,addr_bytes=addr[i])
    if v == 'auto' :
        v = float(input('enter holding voltage (V) : '))
    if t == 'auto' :
        t = int(input('enter holding time (s) : '))
    
    print('starting trial (' + str(v) + ',' + str(t) + ')')
    sel_flag = [False,False,False,False]
    set_outs(v,v,v,v)
    start = time.time()
    while time.time() - start < t :
        i1,i2,i3,i4 = read_currents()
        if abs(i1) > threshold :
            set_out1(0)
            sel_flag[0] = True
            break
        if abs(i2) > threshold :
            set_out2(0)
            sel_flag[1] = True
            break
        if abs(i3) > threshold :
            set_out3(0)
            sel_flag[2] = True
            break
        if abs(i4) > threshold :
            set_out4(0)
            sel_flag[3] = True
            break
    if any(sel_flag) :
        print('SEL detected ~~ you should stop the beam')
        time.sleep(0.1)
    set_nominal()
    
    print('scanning for SEUs')
    data = pd.DataFrame(columns=slots)
    bits = [0] * len(slots)
    check = bytes2bits([pattern] * (1024 * size))
    for i in range(len(slots)) :
        if alt :
            data[slots[i]] = bytes2bits(read_alt(pins[i],size=size,addr_bytes=addr[i]))
        else :
            data[slots[i]] = bytes2bits(read(pins[i],size=size,addr_bytes=addr[i]))
        data[slots[i]] = [x!=y for x,y in zip(data[slots[i]],check)]
        bits[i] = list(data[slots[i]].where(data[slots[i]]==True).dropna().index)
    flips.loc[len(flips.index)] = [v,t] + bits 
    flips.to_csv(trial,index=False)
    return data.sum()
    
def seu_scan(v='auto',t='auto',size=32,pattern=85,threshold=1000) :
    if trial is None:
        print('please use memex.create_trial() to specify a trial csv')
        return 0
    print(trial)
        
    active,awake,addr_bytes = rollcall(show=False)
    pins = [board.D5,board.D6,board.D13,board.D19,board.D26,board.D24,
            board.D25,board.D7,board.D12,board.D16,board.D20,board.D21]
    pins = [x for (x, y) in zip(pins, awake) if y]
    slots = ['A1','A2','A3','B1','B2','B3','C1','C2','C3','D1','D2','D3']
    slots = [x for (x, y) in zip(slots, awake) if y]
    addr = [x for (x, y) in zip(addr_bytes, awake) if y]
    try :
        flips = pd.read_csv(trial)
    except FileNotFoundError :
        flips = pd.DataFrame(columns=['v','t']+slots)
    
    print('scanning for SEUs')
    data = pd.DataFrame(columns=slots)
    bits = [0] * len(slots)
    check = bytes2bits([pattern] * (1024 * size))
    for i in range(len(slots)) :
        data[slots[i]] = bytes2bits(read_alt(pins[i],size=size,addr_bytes=addr[i]))
        data[slots[i]] = [x!=y for x,y in zip(data[slots[i]],check)]
        bits[i] = list(data[slots[i]].where(data[slots[i]]==True).dropna().index)
    flips.loc[len(flips.index)] = [v,t] + bits 
    flips.to_csv(trial,index=False)
    return data.sum()
    
def seu_undo() :
    if trial is None:
        print('please use memex.create_trial() to specify a trial csv')
        return 0
    print(trial)
    flips = pd.read_csv(trial)
    flips = flips.drop(index=len(flips)-1)
    flips.to_csv(trial,index=False)
    
def seu_count() :
    if trial is None:
        print('please use memex.create_trial() to specify a trial csv')
        return 0
    print(trial)
    flips = pd.read_csv(trial)
    total = pd.DataFrame(columns=flips.columns[2:])
    for c in flips.columns[2:] :
        count = 0
        for i in flips.index :
            data = flips[c].iloc[i]
            data = data.split(',')
            if data[0] != '[]' :
                count += len(data)
        print(c,':',count)
        
def create_trial(file) :
    global trial
    trial = file

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

    