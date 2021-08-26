from smbus      import SMBus
from time       import sleep
from datetime   import datetime
from threading  import Thread


from config import DONG, ROOMTYPE, SMARTWATERCARE_SERIALNUMBER
from config import PRESSURESENSOR_LIST
from config import SMARTWATERCARE_SERIALNUMBER
from config import USE_CSV_SAVE, CSV_SAVE_PATH
from config import USE_DB, HOST, USER, PASSWORD, DB, TABLE

from tools.print_t        import print_t as print
from tools.time_lib       import current_time, current_date
from tools.save_as_csv    import save_as_csv
from tools.check_internet import check_internet

from drivers.database import DBSetup

# Conversion factors (from native unit, mbar)
UNITS_Pa     = 100.0 
UNITS_hPa    = 1.0
UNITS_kPa    = 0.1
UNITS_mbar   = 1.0
UNITS_bar    = 0.001
UNITS_atm    = 0.000986923
UNITS_Torr   = 0.750062
UNITS_psi    = 0.014503773773022

# Valid units
UNITS_Centigrade = 1
UNITS_Farenheit  = 2
UNITS_Kelvin     = 3

# Oversampling options
OSR_256  = 0
OSR_512  = 1
OSR_1024 = 2
OSR_2048 = 3
OSR_4096 = 4
OSR_8192 = 5

class M30J2Setup():
    _ADDRESS = 0x28
    _P1      = 1638.3   # 10% * 16383 -A Type # 2^14
    _P2      = 13106.4  # 80% * 16383 -A Type # 2^14
    _P_MAX   = 15.0
    _P_MIN   = 0.0
    
    def __init__(self, tag, interval=0.5):
        self.name     = 'm30j2'
        self.tag      = tag
        self.interval = interval
        
        self.bus                =  SMBus(1)
        self.data               =  None
        self.use_db             =  None
        self.location           = 'None'
        self.status             = 'GOOD'
        
        self.serial_num         =  list(PRESSURESENSOR_LIST.keys())[0]
        self.pressuresensor_num =  PRESSURESENSOR_LIST[self.serial_num][0]
        self.location           =  PRESSURESENSOR_LIST[self.serial_num][1]
        
        if not self.init():
            print('error', '"__init__" -> [ERROR_01] M30J2 Sensor could not be initialized', self.tag)
            self.status = 'ERROR_01'
            
        if not self.read():
            print('error', '"__init__" -> [ERROR_02] M30J2 Sensor read failed', self.tag)
            self.status = 'ERROR_02'

       
    def init(self):
        if self.bus is None:
            print('error', '"init" -> [ERROR_03] can\'t find the bus', self.tag)
            self.status = 'ERROR_03'
            return 0
        
        return True
            
    def read(self, oversampling=OSR_8192):
        if self.bus is None:
            print('error', '"read" -> [ERROR_04] can\'t find the bus', self.tag)
            self.status = 'ERROR_04'
            return 0
        
        if oversampling < OSR_256 or oversampling > OSR_8192:
            print('error', '"read" -> [ERROR_05] Invalid oversampling option', self.tag)
            self.status = 'ERROR_05'
            return 0
        
        sleep(2.5e-6 * 2**(8+oversampling)) # 0.02048
        try:
            read = self.bus.read_i2c_block_data(self._ADDRESS, 0, 4)
        except:
            return 0
        
        if (read[0] & 0xc0) == 0x00:
            d_pressure        = (((read[0] & 0x3f) << 8) | (read[1]))
            d_temperature     = ((read[2] << 3) | (read[3] >> 5))
            self._time        = current_time()
            self._pressure    = (d_pressure - self._P1) * (self._P_MAX - self._P_MIN) / self._P2 + self._P_MIN
            self._temperature = (d_temperature * 200) / 2047 - 50
        
        return True
    
    def pressure(self, conversion=UNITS_bar):
        return self._pressure * conversion

    def temperature(self, conversion=UNITS_Centigrade):
        degC = self._temperature / 100.0
        
        if conversion == UNITS_Farenheit:
            return (9.0/5.0)*degC + 32
        
        elif conversion == UNITS_Kelvin:
            return degC + 273
        
        return degC
    
    def connect_db(self):
        if check_internet():
            if USE_DB:
                try:
                    self.db     = DBSetup(HOST, USER, PASSWORD, DB)
                    self.use_db = True
                    return True
                
                except:
                    self.use_db = False
                    print('error', '"connect_db" -> [ERROR_06] An error occurred while setup the DB', self.tag)
                    self.status = 'ERROR_06'
                    return 0
        else:
            if USE_DB:
                self.use_db = False
                print('warning', '"connect_db" -> Cannot connect to DB because there is no internet connection.', self.tag)

    def loop_thread_start(self):
        thread = Thread(target=self.loop, daemon=True)
        thread.start()
    
    def loop(self):
        error_stack = 0
        while self.status == 'GOOD':
            try:
                sleep(self.interval)
                
                if error_stack > 50:
                    break
                
                if not self.init():
                    error_stack += 1
                    continue
                
                if not self.read():
                    error_stack += 1
                    continue
                
                time        = self._time
                serial_num  = self.serial_num
                pressure    = self._pressure
                temperature = self._temperature
                
                if None in [time, pressure, temperature]:  
                    error_stack += 1
                    continue
                
                if USE_CSV_SAVE:
                    path    = f"{CSV_SAVE_PATH}/{current_date()}_{serial_num}"
                    data    = [ time,   serial_num,   pressure,   temperature]
                    columns = ['time', 'serial_num', 'pressure', 'temperature']
                    save_as_csv(device=self.name, data=data, columns=columns, path=path)
                    
                if self.use_db:
                    location              = self.location
                    pressuresensor_number = self.pressuresensor_num
                    field  = "dong, roomtype, pressuresensor_sn, pressuresensor_number, pressure, temperature, getting_time, location"
                    values = [DONG, ROOMTYPE, serial_num,        pressuresensor_number, pressure, temperature, time,         location]
                    self.db.send(TABLE['m30j2'], field, values)
                    
                print('read', f'{time} | {serial_num:^12} | {pressure:11.6f} bar  | {temperature:11.6f} C', self.tag)
                self.status = 'GOOD'
                
            except OSError:
                error_stack += 1
                continue
            
        print('error', '"loop" -> [ERROR_07] Exit the loop with a fatal error.', self.tag)   
        self.status = 'ERROR_07'
        # To do : Send error message to db
        # time       = current_time()
        # serial_num = self.serial_num
        # error_code = ''
        
        # if self.use_db:
        #     field  = "time, serial_num, error_code"
        #     values = [time, serial_num, error_code]
        #     self.db.send(TABLE, field, values)
        
        while True:
            if not self.init():
                continue
                
            if not self.read():
                continue
            
            print('log', 'Restart the loop.')   
            self.status = 'GOOD'
            break
        
        self.loop_thread_start()