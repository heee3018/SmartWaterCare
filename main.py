from config import *
from tools.print_t import print_t as print

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
        
        
        
    return True

def main():
    while True:
        pass

if __name__ == '__main__':
    try:
        if init():
            main()
        else:
            pass
        
    except KeyboardInterrupt:
        print('log', 'Keyboard interrupted.')