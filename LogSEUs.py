# import packages

import memex
import time
import board
import busio
import digitalio

import adafruit_mcp4725 # for dac
import adafruit_ads1x15.ads1115 as ADS # for adc
from adafruit_ads1x15.analog_in import AnalogIn # for adc
import adafruit_ina260 # for power sensor
import gpiozero # for rgb led

# experiment configuration

pattern = 0 # data pattern to use (0 to 255)
v_nom = 3.3 # nominal operating voltage of SRAMs
v_hold = 0.6 # voltage to hold at during trials
t_hold = 60 # length of each trial
save_file = "/home/pi/MemEx/data/sram/seu.csv" # file location to store data
puf = True
spi_hz = 5000000 # recommended max spi rate: 5 MHz

# init devices

i2c = busio.I2C(board.SCL, board.SDA)
spi = busio.SPI(board.SCLK,MOSI=board.MOSI,MISO=board.MISO)
spi.try_lock()
spi.configure(baudrate=spi_hz)
spi.unlock()

spi_disable = digitalio.DigitalInOut(board.D24) # init spi_disable pin
spi_disable.direction = digitalio.Direction.OUTPUT # set to output
spi_disable.value = False # initial value

try:
    led = gpiozero.RGBLED(red=17,green=27,blue=22,pwm=True) # init led
except:
    led.close()
    led = gpiozero.RGBLED(red=17,green=27,blue=22,pwm=True) # init led

dac = adafruit_mcp4725.MCP4725(i2c) # init dac
led.color = (0,0,1) # blue
memex.set_voltage(v_nom)

led.color = (0,0,0) # off
adc = ADS.ADS1115(i2c) # init adc
a0 = AnalogIn(adc, ADS.P0) # channel 0
a1 = AnalogIn(adc, ADS.P1) # channel 1
a2 = AnalogIn(adc, ADS.P2) # channel 2
print("v_nom:",a0.voltage)

m1 = memex.sram(spi,cs=board.D14,name="M1") # init m1
m2 = memex.sram(spi,cs=board.D15,name="M2") # init m2
m3 = memex.sram(spi,cs=board.D18,name="M3") # init m3
m1.fill(pattern)
m2.fill(pattern)
m3.fill(pattern)
print(m1.name + " status:",m1.read_status())
print(m2.name + " status:",m2.read_status())
print(m3.name + " status:",m3.read_status())

# main loop

# script config
timeout = 3600 * 4

# set nominal voltage
led.color = (0,0,1) # blue for setting voltage
spi_disable.value = False
m1.cs.value = True
m2.cs.value = True
m3.cs.value = True
memex.set_voltage(v_nom)

#pp = ProgressPlot(line_names = [m1.name,m2.name,m3.name])
header = ["Timestamp(s)",
          "DataPattern(Byte)",
          "ActualVoltage(V)",
          "ActualTime(s)",
          m1.name + "Faults(#)",
          m2.name + "Faults(#)",
          m3.name + "Faults(#)"]
print(*header,sep='\t')
start = time.time()

while time.time() - start < timeout:
    if puf:
        # set voltage to 0
        led.color = (0,0,1) # blue for setting voltage
        spi_disable.value = True
        m1.cs.value = False
        m2.cs.value = False
        m3.cs.value = False
        v_puf = memex.set_voltage(0)
        
        # wait 1 second
        led.color = (0,1,0) # green for waiting
        time.sleep(1)
        
        # set nominal voltage
        led.color = (0,0,1) # blue for setting voltage
        spi_disable.value = False
        m1.cs.value = True
        m2.cs.value = True
        m3.cs.value = True
        memex.set_voltage(v_nom)
        
        # save puf
        led.color = (1,0,0) # red for writing to harddrive
        timestamp = memex.timestamp()
        m1.save(file= "/home/pi/MemEx/data/sram/puf/" + m1.name + "_puf_" + str(timestamp) + ".csv")
        m2.save(file= "/home/pi/MemEx/data/sram/puf/" + m2.name + "_puf_" + str(timestamp) + ".csv")
        m3.save(file= "/home/pi/MemEx/data/sram/puf/" + m3.name + "_puf_" + str(timestamp) + ".csv")
    
    # fill with pattern
    led.color = (1,1,1) # white for comms with dut
    m1.fill(pattern)
    m2.fill(pattern)
    m3.fill(pattern)
    
    # set holding voltage
    led.color = (0,0,1) # blue for setting voltage
    spi_disable.value = True
    m1.cs.value = False
    m2.cs.value = False
    m3.cs.value = False
    v_actual = memex.set_voltage(v_hold)
    
    # delay for t_hold
    trial_start = time.time()
    led.color = (0,1,0) # green for waiting
    time.sleep(t_hold)
    
    # set nominal voltage
    led.color = (0,0,1) # blue for setting voltage
    t_actual = time.time() - trial_start
    spi_disable.value = False
    m1.cs.value = True
    m2.cs.value = True
    m3.cs.value = True
    memex.set_voltage(v_nom)
    
    # get data
    led.color = (1,1,1) # white for comms with dut
    faults1 = m1.check(pattern)
    faults2 = m2.check(pattern)
    faults3 = m3.check(pattern)
    
    # save and show data
    led.color = (1,0,0) # red for writing to harddrive
    data = [memex.timestamp(),
            pattern,
            v_actual,
            t_actual,
            faults1,
            faults2,
            faults3]
    memex.log(data,header,file=save_file)
    print(*data,sep='\t')
    
     # update graph
    #pp.update([[faults1,faults2,faults3]])
    
led.color = (0,0,0) # off
#pp.finalize()
