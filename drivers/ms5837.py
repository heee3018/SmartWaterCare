from smbus      import SMBus
from time       import sleep
from threading  import Thread

from config import DONG, ROOMTYPE, SMARTWATERCARE_SERIALNUMBER
from config import PRESSURESENSOR_LIST
from config import USE_CSV_SAVE, CSV_SAVE_PATH
from config import USE_DB, HOST, USER, PASSWORD, DB, TABLE

from tools.print_t        import print_t as print
from tools.time_lib       import current_time, current_date
from tools.save_as_csv    import save_as_csv
from tools.check_internet import check_internet

from drivers.database import DBSetup

# Models
MODEL_02BA = 0
MODEL_30BA = 1

# Oversampling options
OSR_256  = 0
OSR_512  = 1
OSR_1024 = 2
OSR_2048 = 3
OSR_4096 = 4
OSR_8192 = 5

# kg/m^3 convenience
DENSITY_FRESHWATER = 997
DENSITY_SALTWATER = 1029

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


class MS5837Setup():
    _MS5837_ADDR             = 0x76  
    _MS5837_RESET            = 0x1E
    _MS5837_ADC_READ         = 0x00
    _MS5837_PROM_READ        = 0xA0
    _MS5837_CONVERT_D1_256   = 0x40
    _MS5837_CONVERT_D2_256   = 0x50
            
    def __init__(self, tag, interval=0.5, bus=1):
        self.name     = 'ms5837'
        self.tag      =  tag
        self.interval =  interval
        
        self.data       =  None
        self.use_db     =  None
        self.location   = 'None'
        self.status     = 'GOOD'
        
        self._model = MODEL_30BA
        
        self.serial_num         = list(PRESSURESENSOR_LIST.keys())[0]
        self.pressuresensor_num = PRESSURESENSOR_LIST[self.serial_num][0]
        self.location           = PRESSURESENSOR_LIST[self.serial_num][1]
        
        try:
            self._bus = SMBus(bus)
        except:
            print('error', f'"init" -> [ERROR_00] Bus {bus} is not available. Available busses are listed as /dev/i2c*', self.tag)
            self.status = 'ERROR_00'
            self._bus = None
            
        self._fluidDensity = DENSITY_FRESHWATER
        self._pressure     = 0
        self._temperature  = 0
        self._D1           = 0
        self._D2           = 0
        
        if not self.init():
            print('error', '"__init__" -> [ERROR_01] MS5837 Sensor could not be initialized', self.tag)
            self.status = 'ERROR_01'
        
        if not self.read():
            print('error', '"__init__" -> [ERROR_02] MS5837 Sensor read failed', self.tag)
            self.status = 'ERROR_02'

        
    def init(self):
        if self._bus is None:
            print('error', '"init" -> [ERROR_03] can\'t find the bus', self.tag)
            self.status = 'ERROR_03'
            return 0
        try:
            self._bus.write_byte(self._MS5837_ADDR, self._MS5837_RESET)
        except:
            return 0
        # Wait for reset to complete
        sleep(0.01)
        
        self._C = []
        
        # Read calibration values and CRC
        for i in range(7):
            c = self._bus.read_word_data(self._MS5837_ADDR, self._MS5837_PROM_READ + 2*i)
            c =  ((c & 0xFF) << 8) | (c >> 8) # SMBus is little-endian for word transfers, we need to swap MSB and LSB
            self._C.append(c)
                        
        crc = (self._C[0] & 0xF000) >> 12
        if crc != self._crc4(self._C):
            print('error', '"init" -> [ERROR_04] PROM read error, CRC failed.', self.tag)
            self.status = 'ERROR_04'
            return 0
        
        return True
        
    def read(self, oversampling=OSR_8192):
        if self._bus is None:
            print('error', '"read" -> [ERROR_05] can\'t find the bus', self.tag)
            self.status = 'ERROR_05'
            return 0
        
        if oversampling < OSR_256 or oversampling > OSR_8192:
            print('error', '"read" -> [ERROR_06] Invalid oversampling option', self.tag)
            self.status = 'ERROR_06'
            return 0
        
        # Request D1 conversion (temperature)
        try:
            self._bus.write_byte(self._MS5837_ADDR, self._MS5837_CONVERT_D1_256 + 2*oversampling)
        except:
            return 0
        # Maximum conversion time increases linearly with oversampling
        # max time (seconds) ~= 2.2e-6(x) where x = OSR = (2^8, 2^9, ..., 2^13)
        # We use 2.5e-6 for some overhead
        sleep(2.5e-6 * 2**(8+oversampling))
        
        d = self._bus.read_i2c_block_data(self._MS5837_ADDR, self._MS5837_ADC_READ, 3)
        self._D1 = d[0] << 16 | d[1] << 8 | d[2]
        
        # Request D2 conversion (pressure)
        self._bus.write_byte(self._MS5837_ADDR, self._MS5837_CONVERT_D2_256 + 2*oversampling)
    
        # As above
        sleep(2.5e-6 * 2**(8+oversampling))
 
        d = self._bus.read_i2c_block_data(self._MS5837_ADDR, self._MS5837_ADC_READ, 3)
        self._D2 = d[0] << 16 | d[1] << 8 | d[2]

        # Calculate compensated pressure and temperature
        # using raw ADC values and internal calibration
        self._calculate()
        
        return True
    
    def setFluidDensity(self, denisty):
        self._fluidDensity = denisty
    
    def pressure(self, conversion=UNITS_bar):
        # Pressure in requested units
        # mbar * conversion
        return self._pressure * conversion
        
    def temperature(self, conversion=UNITS_Centigrade):
        # Temperature in requested units
        # default degrees C
        degC = self._temperature / 100.0
        
        if conversion == UNITS_Farenheit:
            return (9.0/5.0)*degC + 32
        
        elif conversion == UNITS_Kelvin:
            return degC + 273
        
        return degC
        
    def depth(self):
        # Depth relative to MSL pressure in given fluid density
        return (self.pressure(UNITS_Pa)-101300)/(self._fluidDensity*9.80665)
    
    def altitude(self):
        # Altitude relative to MSL pressure
        return (1-pow((self.pressure()/1013.25),.190284))*145366.45*.3048        
    
    def _calculate(self):
        # Cribbed from datasheet
        OFFi = 0
        SENSi = 0
        Ti = 0

        dT = self._D2-self._C[5]*256
        if self._model == MODEL_02BA:
            SENS = self._C[1]*65536+(self._C[3]*dT)/128
            OFF = self._C[2]*131072+(self._C[4]*dT)/64
            self._pressure = (self._D1*SENS/(2097152)-OFF)/(32768)
        else:
            SENS = self._C[1]*32768+(self._C[3]*dT)/256
            OFF = self._C[2]*65536+(self._C[4]*dT)/128
            self._pressure = (self._D1*SENS/(2097152)-OFF)/(8192)
        
        self._temperature = 2000+dT*self._C[6]/8388608

        # Second order compensation
        if self._model == MODEL_02BA:
            if (self._temperature/100) < 20: # Low temp
                Ti = (11*dT*dT)/(34359738368)
                OFFi = (31*(self._temperature-2000)*(self._temperature-2000))/8
                SENSi = (63*(self._temperature-2000)*(self._temperature-2000))/32
                
        else:
            if (self._temperature/100) < 20: # Low temp
                Ti = (3*dT*dT)/(8589934592)
                OFFi = (3*(self._temperature-2000)*(self._temperature-2000))/2
                SENSi = (5*(self._temperature-2000)*(self._temperature-2000))/8
                if (self._temperature/100) < -15: # Very low temp
                    OFFi = OFFi+7*(self._temperature+1500)*(self._temperature+1500)
                    SENSi = SENSi+4*(self._temperature+1500)*(self._temperature+1500)
            elif (self._temperature/100) >= 20: # High temp
                Ti = 2*(dT*dT)/(137438953472)
                OFFi = (1*(self._temperature-2000)*(self._temperature-2000))/16
                SENSi = 0
        
        OFF2 = OFF-OFFi
        SENS2 = SENS-SENSi
        
        if self._model == MODEL_02BA:
            self._time        = current_time()
            self._temperature = (self._temperature-Ti)
            self._pressure = (((self._D1*SENS2)/2097152-OFF2)/32768)/100.0
        else:
            self._time        = current_time()
            self._temperature = (self._temperature-Ti)
            self._pressure = (((self._D1*SENS2)/2097152-OFF2)/8192)/10.0   
        
    def _crc4(self, n_prom):
        # Cribbed from datasheet
        n_rem = 0
        
        n_prom[0] = ((n_prom[0]) & 0x0FFF)
        n_prom.append(0)
    
        for i in range(16):
            if i%2 == 1:
                n_rem ^= ((n_prom[i>>1]) & 0x00FF)
            else:
                n_rem ^= (n_prom[i>>1] >> 8)
                
            for n_bit in range(8,0,-1):
                if n_rem & 0x8000:
                    n_rem = (n_rem << 1) ^ 0x3000
                else:
                    n_rem = (n_rem << 1)

        n_rem = ((n_rem >> 12) & 0x000F)
        
        self.n_prom = n_prom
        self.n_rem = n_rem
    
        return n_rem ^ 0x00
    
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
                pressure    = self.pressure(UNITS_bar)
                temperature = self.temperature(UNITS_Centigrade)
                
                if USE_CSV_SAVE:
                    path    = f"{CSV_SAVE_PATH}/{current_date()}_{self.serial_num}"
                    data    = [ time,   serial_num,   pressure,   temperature]
                    columns = ['time', 'serial_num', 'pressure', 'temperature']
                    save_as_csv(device=self.name, data=data, columns=columns, path=path)
                    
                if self.use_db:
                    location              = self.location
                    pressuresensor_number = self.pressuresensor_num
                    field  = "dong, roomtype, pressuresensor_sn, pressuresensor_number, pressure, temperature, getting_time, location"
                    values = [DONG, ROOMTYPE, serial_num,        pressuresensor_number, pressure, temperature, time,         location]
                    self.db.send(TABLE['m30j2'], field, values)
                    # MS5837 No Table !!
                    
                print('read', f'{time} | {serial_num:^12} | {pressure:11.6f} bar | {temperature:11.6f} C', self.tag)
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
        
    
    