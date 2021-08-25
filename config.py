DONG                          = "201"
ROOMTYPE                      = "E"
SMARTWATERCARE_SERIALNUMBER   = "PNC-SWCM-" + DONG + ROOMTYPE
SMARTWATERCARE_STATUS         = 0     # 0: 정상동작, 1:통신이상
SMARTWATERCARE_ERRORCODE      = ''

PRESSURESENSOR_LIST = {
    '8-052121B401': [1, 'AP_WATER'] 
}

WATERMETER_LIST = {
    '20201307'    : [1, 'AP_WATER'],
    '20201312'    : [2, 'AP_HEATINGWATER'],
    '20201314'    : [3, 'FIRSTFLOOR_KITCHEN_BASIN'],
    '20201315'    : [4, 'FIRSTFLOOR_KITCHEN_BUILTINWASHER'],
    '20201316'    : [5, 'FIRSTFLOOR_RESTROOM_TOILET'],
    '20201317'    : [6, 'FIRSTFLOOR_RESTROOM_WASHBASIN'],
    '21070109'    : [7, 'FIRSTFLOOR_RESTROOM_SHOWERS'],
    '21070110'    : [8, 'FIRSTFLOOR_UTILITYROOM_WASHER'],
    '20201309'    : [9, 'FIRSTFLOOR_OUTDOOR']
}

MAXIMUM_CONNECTABLE_USB_LIST = ['/dev/ttyUSB'+str(i) for i in range(14)]
connected_usb_list = []
available_usb_list = []

USE_CSV_SAVE  = True
CSV_SAVE_PATH = '/home/pi/Desktop/CSV_Files'

USE_DB   = True
HOST     = 'smartwatercare.net' # 13.125.158.130
USER     = 'kwater01'
PASSWORD = '1234'
DB       = 'smartwatercare'
TABLE    = {
    'lxc'   :'WaterMeter',
    'm30j2' :'PressureSensor'}

USE_REST_API = False