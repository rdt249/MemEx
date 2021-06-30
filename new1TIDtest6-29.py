print('Importing packages...')
from memex import set_voltage_4
from memex import vramp
from memex import sram
from multiprocessing import Process, Queue, Event, Manager
import adafruit_ina219
import numpy as np
import pandas as pd
import board
import RPi.GPIO as GPIO
import busio
import time
import os



'''
Helper functions
'''
GPIO.setup(26, GPIO.OUT)

#toggle OE
def toggle_oe(state):
    if state == 1:
        GPIO.output(26, 1)
        
    else:
        GPIO.output(26, 0)
        
#check sensor status      
def check_status(multiprocess = True,
                 sensor = adafruit_ina219.INA219(busio.I2C(board.SCL, board.SDA))):
    
    samples = []
    t0 = time.time()
    i = 0
    print('taking data')
    while not quit.is_set():
        
        volt = sensor.bus_voltage
        current = sensor.current
#         print('current: '+str(current))
        samples.append([volt, current]) 
        
    
    print('data taking complete')
    
    df = pd.DataFrame(samples, columns = ['Voltage','Current'])
    df = df.query('Current > 0.2')
    avg_current = df['Current'].mean()
    
    df1 = pd.DataFrame()
    
    df1[memory.name+'_'+t_start] = [avg_current]
    
    if multiprocess:
        Q.put(df1)

#take idle current
def idle(samp_time, sensor = adafruit_ina219.INA219(busio.I2C(board.SCL, board.SDA))):
    
    t0 = time.time()
    t_end = t0 + samp_time
    
    samples = []
    
    while True:
        
        volt = sensor.bus_voltage
        current = sensor.current
        
        samples.append([volt, current])
        
        if time.time() > t_end:
            break
        
     
    df = pd.DataFrame(samples, columns = ['Voltage','Current'])
    avg_current = df['Current'].mean()
    
    return avg_current 

#fill memory with a pattern
def fill_mem(memory, pattern):
    print('filling '+memory.name)
    memory.fill(pattern)
    foundit.set()
    
#check memory pattern
def check_mem(memory, pattern, return_dict):
    print('checking '+memory.name)
    flips = memory.check(pattern)
    print(str(flips)+' bits different')
    return_dict['bits'] = flips
    foundit.set()

#led functions    
def blink(pin):
#     GPIO.setmode(GPIO.BOARD)
    
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    
def turnOff(pin):
#     GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    

'''
variables
'''

#Name of the DUT
device = 'microchip'
path = '~/MemEx/data/sram/data_6-29/'
pattern = 0x55

redPin   = 22
greenPin = 27
bluePin  = 17

Q = Queue()

'''
Initialize SRAM
'''
print('Initializing SRAMs...')

blink(greenPin)

GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD 

#set voltage for memory
set_voltage_4({'a':3.3})

#set OE high
toggle_oe(1)

#set hold pin high
GPIO.setup(19, GPIO.OUT) # set a port/pin as an output   
GPIO.output(19, 1)       # set port/pin value to 1/GPIO.HIGH/True  

spi = busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO)
spi.try_lock()
spi.configure(baudrate=1000000)
spi.unlock()

m1 = sram(spi,cs=board.D5, name="M1", size=32, bit_address=16) # init m1
m2 = sram(spi,cs=board.D6, name="M2", size=32, bit_address=16) # init m1
m3 = sram(spi,cs=board.D13, name="M3", size=32, bit_address=16) # init m1

#bias to zero
bias = 0
toggle_oe(0)
set_voltage_4({'a':bias})

print('Initialization complete!')

while True:
    
    answer1 = input('\n Initialization / Test complete, SRAM is biased to ' + str(bias) + 'V \n Run again? (y/n)')
    
    if answer1 == 'y':
        print('Starting data collection!')
        pass
    
    else:
        print('ending script!')
        turnOff(greenPin)
        break
    dosage = input('enter the dosage')
    if not os.path.exists(path+dosage+'/'):
        os.mkdir('/home/pi/MemEx/data/sram/data_6-29/'+dosage+'/')
    
    turnOff(greenPin)
    blink(redPin)
    
    t_start = time.ctime()[4::]
        
    '''
    Read PUF:
        Power cycle
        Read inital state
        repeat x times
        save PUF csvs
    '''
    #open csv
    df_PUF = pd.DataFrame()

    #sample PUF x times
    X = 10
    save_size = 1
    for i in range(X):

        print('\n Sampling SRAM %s/%s times...'%(str(i+1), str(X)))

        #voltage ramp
        toggle_oe(0)
        set_voltage_4({'a':0})
        vramp(0, 3.3, step_size=8, channel = 'a')
        toggle_oe(1)

        #save to dataframe
        data1 = m1.save_list(save_size)
        df_PUF['m1 TID @ '+time.ctime()[4::].split(' ')[-2]] = data1
        data2 = m2.save_list(save_size)
        df_PUF['m2 TID @ '+time.ctime()[4::].split(' ')[-2]] = data2
        data3 = m3.save_list(save_size)
        df_PUF['m3 TID @ '+time.ctime()[4::].split(' ')[-2]] = data3
        
    save_name = path+dosage+'/'+device+'_PUF_'+t_start.split(' ')[-2]+'.csv'
    df_PUF.to_csv(save_name, index=False)
    print('PUF saved to: '+save_name)

    #save csv

    '''
    Write test:
        Write block
        Sample current
        Repeat X times
    '''
    #open containing write, read, and leakage current
    try:
        df_rwl = pd.read_csv(path+device+'_rwl.csv', index_col=[0,1])
    except:
        arrays = [np.array(['microchip','microchip','microchip','microchip']),
        np.array(['Write Current [mA]', 'Read Current [mA]','Idle Current [mA]', 'Flipped bits'])]

        c = pd.DataFrame(index=['Write Current [mA]', 'Read Current [mA]', 'Idle Current [mA]'])

        s = pd.DataFrame(index=arrays)
        df_rwl = pd.merge(s.reset_index(), c, left_on='level_1', right_index=True).groupby(['level_0', 'level_1']).sum()
        df_rwl.index.names = ['Manufacturer','Data']

    for memory in [m1,m2,m3]:
        print('\n Filling to memory %s and sampling current'%(memory.name))

        data = Process(target=check_status, args=(True,))
        task = Process(target=fill_mem, args=(memory, pattern))

        quit = Event()
        foundit = Event()

        data.start()
        task.start()

        foundit.wait()
        quit.set()

        df_write = Q.get()

        current_column = df_write.columns[0]
        df_rwl.loc[(device, 'Write Current [mA]'), current_column] = df_write.iloc[0][current_column]
        


    '''
    Read test:
        Read block
        Sample current
        Count faults
        Repeat X times
    '''
    for memory in [m1,m2,m3]:
        print('\n Checking memory %s and sampling current'%(memory.name))
        
        manager = Manager()
        return_dict = manager.dict()
        
        data = Process(target=check_status, args=(True,))
        task = Process(target=check_mem, args=(memory, pattern, return_dict))

        quit = Event()
        foundit = Event()

        data.start()
        task.start()

        foundit.wait()
        quit.set()

        df_write = Q.get()


        current_column = df_write.columns[0]
        df_rwl.loc[(device, 'Read Current [mA]'), current_column] = df_write.iloc[0][current_column]
        
        df_rwl.loc[(device, 'Flipped bits'), current_column] = return_dict['bits']


    '''
    Dosing and leakage:
        Ground VRAM (0V)
        wait for trigger
        nominal VRAM (3.3V)
        sample current
        update test data csv
    '''
    print('\n Checking idle current')

    toggle_oe(0)
    set_voltage_4({'a':0})
    time.sleep(1)
    set_voltage_4({'a':3.3})

    #sample current

    idle_current = idle(3)

    df_rwl.loc[(device, 'Idle Current [mA]'), 'M1_'+t_start] = idle_current
    df_rwl.loc[(device, 'Idle Current [mA]'), 'M2_'+t_start] = idle_current
    df_rwl.loc[(device, 'Idle Current [mA]'), 'M3_'+t_start] = idle_current

    df_rwl.to_csv(path+dosage+'/'+device+'_rwl.csv')

    print('test run complete!')
    turnOff(redPin)
    blink(greenPin)









