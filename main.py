import os
from time import time, sleep

import config
from config import SMARTWATERCARE_SERIALNUMBER, WATERMETER_LIST
from config import USE_CSV_SAVE, USE_DB

from tools.print_t        import print_t as print
from tools.time_lib       import time_sync, time_format
from tools.check_internet import check_internet

from drivers.lxc    import LXCSetup
from drivers.m30j2  import M30J2Setup
from drivers.ms5837 import MS5837Setup

STOP_WATCH_INTERVAL = 10
start_time = time()

def init():  
    if USE_CSV_SAVE:
        print('log', 'Use [USE_CSV_SAVE] option')
    else:
        print('warning', '[USE_CSV_SAVE] option is off')
        
    if USE_DB:
        print('log', 'Use [USE_DB] option')
    else:
        print('warning', '[USE_DB] option is off')
    
    if check_internet():
        print('log', 'Connected to the Internet.')
        time_sync()
        print('log', 'Synchronized the time')
    else:
        print('warning', 'No internet connection')
    
    print('log', f'SMART WATER CARE SERIAL NUMBER : {SMARTWATERCARE_SERIALNUMBER}')
    
    # LXC Serial number search list
    print('log', 'LXC Serial number search list :')
    for i, serial_num in enumerate(list(WATERMETER_LIST.keys()), start=1):
        print('log', f'  {i}. {serial_num} : {WATERMETER_LIST[serial_num]}')
    
    # USB list update
    print('log', 'USB connected by Raspberry pi :')
    config.connected_usb_list = os.popen('ls /dev/ttyUSB*').read().split('\n')[:-1]
    for i, usb in enumerate(config.connected_usb_list, start=1):
        print('log', f'  {i}. {usb[5:]}')
        
    # Devices setup
    devices = list()
    devices.append(MS5837Setup(tag='I2C1', interval=0.5))
    #devices.append(M30J2Setup(tag='I2C1', interval=0.5))
    for usb in config.connected_usb_list:
        devices.append(LXCSetup(tag=usb[8:], port=usb))
    
    # Devices Connect db
    for dev in devices:
        if dev.connect_db():
            print('success', 'Successfully connected to the DB.', dev.tag)
    
    # LXC Connect serial
    for dev in devices:
        if dev.name == 'lxc':
            if dev.connect_serial(mode='first'):
                print('success', 'Successfully connected to the Serial port.', dev.tag)
                      
    # LXC Serial number search
    threads = list()
    for dev in devices:
        if dev.name == 'lxc' and dev.status == 'GOOD':
            thread = dev.find_thread_start()
            threads.append(thread)
            print('log', 'Start address search.', dev.tag)
    for thread in threads:
        thread.join()
    
    # Devices status 
    for dev in devices:
        print('log', f'Status of {dev.tag} : {dev.status}')

    # Start loop
    for dev in devices:
        if dev.status == 'GOOD': 
            dev.loop_thread_start()
            print('log', f'Loop thread start', dev.tag)
            
    return True

def main():
    while True:
        op_time = time_format(time()-start_time)
        print('log', f'Operating time : {op_time}')
        sleep(STOP_WATCH_INTERVAL)


if __name__ == '__main__':
    try:
        if init():
            main()
        
    except KeyboardInterrupt:
        print('log', 'Keyboard interrupted.')
