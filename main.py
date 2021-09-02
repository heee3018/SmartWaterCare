import os
from time import time, sleep

import config
from config import USE_LXC, USE_MS5837, USE_M30J2
from config import DEVICES, STOPWATCH_INTERVAL
from config import USE_CSV_SAVE, USE_DB

from tools.print_t        import print_t as print
from tools.time_lib       import time_sync, time_format
from tools.check_internet import check_internet

from drivers.lxc    import LXCSetup
from drivers.m30j2  import M30J2Setup
from drivers.ms5837 import MS5837Setup

def init():  
    
    # Check if the Raspberry Pi is connected to the Internet.
    if check_internet():
        print('log', 'Connected to the Internet.')
        time_sync()
        print('log', 'Synchronized the time')
    else:
        print('warning', 'No internet connection')
        
    # Check whether to save the data as a CSV file.
    if USE_CSV_SAVE:
        print('log', 'Use [USE_CSV_SAVE] option')
    else:
        print('warning', '[USE_CSV_SAVE] option is off')
    
    # Checks whether to send data to the connected DB server. 
    if USE_DB:
        print('log', 'Use [USE_DB] option')
    else:
        print('warning', '[USE_DB] option is off')

    if USE_LXC:
        # LXC Serial number list
        print('log', 'LXC Serial number search list :')
        for serial_num in list(DEVICES['lxc'].keys()):
            print('log', f'  - {DEVICES["lxc"][serial_num][0]}  {DEVICES["lxc"][serial_num][1]}  {serial_num}  {DEVICES["lxc"][serial_num][2]}')
    
        # USB list update
        print('log', 'USB connected by Raspberry pi :')
        config.connected_usb_list = os.popen('ls /dev/ttyUSB*').read().split('\n')[:-1]
        for i, usb in enumerate(config.connected_usb_list, start=1):
            print('log', f'  {i}. {usb[5:]}')
        
    # Devices setup
    devices = list()
    if USE_MS5837 and 'ms5837' in list(DEVICES.keys()):
        devices.append(MS5837Setup(tag='I2C0', device=DEVICES['ms5837'], interval=0.5))
    if USE_M30J2 and 'm30j2' in list(DEVICES.keys()):
        devices.append(M30J2Setup(tag='I2C1', device=DEVICES['m30j2'], interval=0.5))
    if USE_LXC and 'lxc' in list(DEVICES.keys()):
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
    start_time = time()
    while True:
        op_time = time_format(time()-start_time)
        print('log', f'Operating time : {op_time}')
        sleep(STOPWATCH_INTERVAL)


if __name__ == '__main__':
    try:
        if init():
            main()
        else:
            print('error', 'A problem occurred during initialization.')
        
    except KeyboardInterrupt:
        print('log', 'Keyboard interrupted.')
