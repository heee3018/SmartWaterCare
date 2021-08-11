from time import time, sleep
from config import CHOOSE_ONE_USB, USE_CSV_SAVE, USE_DB
from tools.print_t        import print_t as print
from tools.time_sync      import time_sync
from tools.time_format    import time_format
from tools.check_internet import check_internet
from drivers.lxc    import LXCSetup
from drivers.m30j2  import M30J2Setup
from drivers.ms5837 import MS5837Setup

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
    
    # Devices setup
    try:
        devices = list()
        devices.append(MS5837Setup(tag='I2C_0', interval=0.5))
        devices.append(M30J2Setup(tag='I2C_1', interval=0.5))
        devices.append(LXCSetup(tag='USB_0', port='/dev/ttyUSB0'))
        devices.append(LXCSetup(tag='USB_1', port='/dev/ttyUSB1'))
        devices.append(LXCSetup(tag='USB_2', port='/dev/ttyUSB2'))
        devices.append(LXCSetup(tag='USB_3', port='/dev/ttyUSB3'))
        devices.append(LXCSetup(tag='USB_4', port='/dev/ttyUSB4'))
        devices.append(LXCSetup(tag='USB_5', port='/dev/ttyUSB5'))
        devices.append(LXCSetup(tag='USB_6', port='/dev/ttyUSB6'))
    except:
        print('error', 'Failed to setup devices')
        return False
    
    # LXC Serial number search
    threads = list()
    for dev in devices:
        if dev.name == 'lxc':
            if dev.connect_port():
                thread = dev.start_search_thread()
                threads.append(thread)
                
    for thread in threads:
        thread.join()
    
    # Devices state
    for dev in devices:
        # if dev.name == 'lxc':
        print(f"{'[LOG]':>10} {dev.tag} - {dev.state}")
            
    for dev in devices:
        if dev.state == 'enabled': 
            dev.start_read_thread()
            
    return True

def main():
    start_time = time()
    while True:
        op_time = time_format(time()-start_time)
        sleep(60)
        print('log', f'Operating time: {op_time}')

if __name__ == '__main__':
    try:
        if init():
            main()
        else:
            pass
        
    except KeyboardInterrupt:
        print('log', 'Keyboard interrupted.')