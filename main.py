import os
from time import time, sleep
from config import SMARTWATERCARE_SERIAL_NUMBER, ULTRASONIC_WATER_METER_LIST, LXC_SERIAL_NUMBER_LIST
from config import CHOOSE_ONE_USB, USE_CSV_SAVE, USE_DB, LXC_SERIAL_NUMBER_LIST
from tools.print_t        import print_t as print
from tools.time_lib       import time_sync, time_format
from tools.check_internet import check_internet
from drivers.lxc import LXCSetup
# from drivers.m30j2  import M30J2Setup
# from drivers.ms5837 import MS5837Setup

STOP_WATCH_INTERVAL = 5

def init():
    if CHOOSE_ONE_USB:
        print('log', 'Use [CHOOSE_ONE_USB] option')
        
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
    
    print('log', f'SMART WATER CARE SERIAL NUMBER : {SMARTWATERCARE_SERIAL_NUMBER}')
    
    print('log', 'LXC Serial number search list :')
    for i, serial_num in enumerate(LXC_SERIAL_NUMBER_LIST, start=1):
        print('log', f'  {i}. {serial_num} : {ULTRASONIC_WATER_METER_LIST[serial_num]}')
    
    print('log', 'USB connected by Raspberry pi :')
    usb_list = os.popen('ls /dev/ttyUSB*').read().split('\n')[:-1]
    for i, usb in enumerate(usb_list, start=1):
        print('log', f'  {i}. {usb[5:]}')
        
    # Devices setup
    try:
        devices = list()
        # devices.append(MS5837Setup(tag='I2C_0', interval=0.5))
        # devices.append(M30J2Setup(tag='I2C_1', interval=0.5))
        devices.append(LXCSetup(tag='USB_0', port='/dev/ttyUSB0'))
        devices.append(LXCSetup(tag='USB_1', port='/dev/ttyUSB1'))
        devices.append(LXCSetup(tag='USB_2', port='/dev/ttyUSB2'))
        devices.append(LXCSetup(tag='USB_3', port='/dev/ttyUSB3'))
        devices.append(LXCSetup(tag='USB_4', port='/dev/ttyUSB4'))
        devices.append(LXCSetup(tag='USB_5', port='/dev/ttyUSB5'))
        devices.append(LXCSetup(tag='USB_6', port='/dev/ttyUSB6'))
    except:
        print('error', 'Failed to setup devices')
        return 0
    
    # LXC Serial number search
    threads = list()
    for dev in devices:
        if dev.name == 'lxc':
            thread = dev.find_thread_start()
            threads.append(thread)
            print('log', 'Start address search.', dev.tag)
    for thread in threads:
        thread.join()
    
    # Devices state
    for dev in devices:
        if dev.name == 'lxc':
            print('log' f'{dev.status} : {dev.location}', dev.tag)

    # Start loop
    for dev in devices:
        if dev.status == 'GOOD': 
            dev.loop_thread_start()
            
    return True

def main():
    start_time = time()
    while True:
        op_time = time_format(time()-start_time)
        sleep(STOP_WATCH_INTERVAL)
        print('log', f'Operating time: {op_time}')


if __name__ == '__main__':
    try:
        if init():
            main()
        
    except KeyboardInterrupt:
        print('log', 'Keyboard interrupted.')
