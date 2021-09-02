from device_list import DEVICE_LIST

DONG          = "201" # 201, 202, ... TEST
ROOMTYPE      = "E"   # A, B, C, ... 1, 2, ...

DEVICES = DEVICE_LIST[DONG+"-"+ROOMTYPE]

USE_LXC       = True
USE_MS5837    = True
USE_M30J2     = True

USE_DB        = True
USE_CSV_SAVE  = True

STOPWATCH_INTERVAL = 10

MAXIMUM_CONNECTABLE_USB_LIST = ['/dev/ttyUSB'+str(i) for i in range(13)]
connected_usb_list = []
available_usb_list = []

CSV_SAVE_PATH = '/home/pi/Desktop/CSV_Files'

HOST     = 'smartwatercare.net' # 13.125.158.130
USER     = 'kwater01'
PASSWORD = '1234'
DB       = 'smartwatercare'
TABLE    = {
    'lxc'   :'water_meters',
    'm30j2' :'pressure_sensors',
    'ms5837':'pressure_sensors' 
}
