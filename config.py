DONG                          = "201"
ROOMTYPE                      = "E"
SMARTWATERCARE_SERIALNUMBER   = "PNC-SWCM-" + DONG + ROOMTYPE
SMARTWATERCARE_STATUS         = 0     # 0: 정상동작, 1:통신이상
SMARTWATERCARE_ERRORCODE      = ''

USE_LXC    = True
USE_MS5837 = True
USE_M30J2  = True

LOCATION = {
    'AP_WATER'                          : 'AP_water_',                       # 수돗물 인입유량
    'AP_HEATINGWATER'                   : 'AP_heatingwater_',                # 수돗물 급탕메인
    'FIRSTFLOOR_KITCHEN_BASIN'          : 'fstfloor_kitchen_basin_',         # 1층 주방 급수
    'FIRSTFLOOR_KITCHEN_BUILTINWASHER'  : 'fstfloor_kitchen_builtinwasher_', # 1층 주방 빌트인세탁기
    'FIRSTFLOOR_RESTROOM_TOILET'        : 'fstfloor_restroom_toilet_',       # 1층 화장실 변기
    'FIRSTFLOOR_RESTROOM_WASHBASIN'     : 'fstfloor_restroom_washbasin_',    # 1층 화장실 세면기
    'FIRSTFLOOR_RESTROOM_SHOWERS'       : 'fstfloor_restroom_showers_',      # 1층 화장실 사워기
    'FIRSTFLOOR_UTILITYROOM_WASHER'     : 'fstfloor_utilityroom_washer_',    # 1층 다용도실_
    'FIRSTFLOOR_OUTDOOR'                : 'fstfloor_outdoor_',               # 1층 옥외
    'SECONDFLOOR_KITCHEN_BASIN'         : 'sndfloor_kitchen_basin_',         # 2층 주방 급수
    'SECONDFLOOR_KITCHEN_BUILTINWASHER' : 'sndfloor_kitchen_builtinwasher_', # 2층 주방 빌트인세탁기
    'SECONDFLOOR_RESTROOM2_TOILET'      : 'sndfloor_restroom2_toilet_',      # 2층 화장실2번 변기
    'SECONDFLOOR_RESTROOM2_WASHBASIN'   : 'sndfloor_restroom2_washbasin_',   # 2층 화장실2번 세면기
    'SECONDFLOOR_RESTROOM2_SHOWERS'     : 'sndfloor_restroom2_showers_',     # 2층 화장실2번 샤워기
    'SECONDFLOOR_RESTROOM3_TOILET'      : 'sndfloor_restroom3_toilet_',      # 2층 화장실3번 변기
    'SECONDFLOOR_RESTROOM3_WASHBASIN'   : 'sndfloor_restroom3_washbasin_',   # 2층 화장실3번 세면기
    'SECONDFLOOR_RESTROOM3_TUB'         : 'sndfloor_restroom3_tub_',         # 2층 화장실3번 욕조
    'SECONDFLOOR_DRESSROOM'             : 'sndfloor_dressroom_',             # 2층 드레스룸 세면기
    'SECONDFLOOR_OUTDOOR'               : 'sndfloor_outdoor_'                # 2층 옥외
}

PRESSURESENSOR_LIST = {
    '8-052121B401': [1, 'AP_WATER'] 
    
}

WATERMETER_LIST = {
    '20201307'    : [1, '25A', 'AP_WATER'],
    '20201312'    : [2, '15A', 'AP_HEATINGWATER'],
    '20201314'    : [3, '15A', 'FIRSTFLOOR_KITCHEN_BASIN'],
    '20201315'    : [4, '15A', 'FIRSTFLOOR_KITCHEN_BUILTINWASHER'],
    '20201316'    : [5, '15A', 'FIRSTFLOOR_RESTROOM_TOILET'],
    '20201317'    : [6, '15A', 'FIRSTFLOOR_RESTROOM_WASHBASIN'],
    '21070109'    : [7, '15A', 'FIRSTFLOOR_RESTROOM_SHOWERS'],
    '21070110'    : [8, '15A', 'FIRSTFLOOR_UTILITYROOM_WASHER'],
    '20201309'    : [9, '15A', 'FIRSTFLOOR_OUTDOOR']
}

MAXIMUM_CONNECTABLE_USB_LIST = ['/dev/ttyUSB'+str(i) for i in range(13)]
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
    'lxc'   :'water_meters',
    'ms5837':'pressure_sensors', 
    'm30j2' :'pressure_sensors'}

USE_REST_API = False