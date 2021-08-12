DONG_NUMBER                  = "201"
HOUSEHOLD_TYPE               = "E"
SMARTWATERCARE_SERIAL_NUMBER = "PNC-SWCM-" + DONG_NUMBER + HOUSEHOLD_TYPE
SMARTWATERCARE_STATUS        = 0     # 0: 정상동작, 1:통신이상
SMARTWATERCARE_ERRORCODE     = ''

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

CHOOSE_ONE_USB         = True

ULTRASONIC_WATER_METER_LIST = {
    '20201307' : 'AP_WATER',
    '20201312' : 'AP_HEATINGWATER',
    '20201314' : 'FIRSTFLOOR_KITCHEN_BASIN',
    '20201315' : 'FIRSTFLOOR_KITCHEN_BUILTINWASHER',
    '20201316' : 'FIRSTFLOOR_RESTROOM_TOILET',
    '20201317' : 'FIRSTFLOOR_RESTROOM_WASHBASIN',
    '21070109' : 'FIRSTFLOOR_RESTROOM_SHOWERS',
    '21070110' : 'FIRSTFLOOR_UTILITYROOM_WASHER'}
LXC_SERIAL_NUMBER_LIST = list(ULTRASONIC_WATER_METER_LIST.keys())

USE_CSV_SAVE  = True
CSV_SAVE_PATH = '/home/pi/Desktop/CSV_Files'

USE_DB   = True
HOST     = 'smartwatercare.net'
USER     = 'kwater01'
PASSWORD = '1234'
DB       = 'kwaterdb'
TABLE    = 'KWATERTABLE'

USE_REST_API = False