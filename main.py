from time import time, sleep
from datetime import datetime, timedelta
from config import CHOOSE_ONE_USB, USE_CSV_SAVE, USE_DB
from tools.print_t import print_t as print
from tools.check_internet import check_internet
from tools.time_synchronization import time_sync
from tools.time import time_format

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
    
    # devices = list()
    # devices.append()
    
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