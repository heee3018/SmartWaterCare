from time      import sleep
from threading import Thread
from serial    import Serial, serialutil

from config    import SERIAL_NUMBER
from config    import USE_CSV_SAVE, CSV_SAVE_PATH
from config    import USE_DB, HOST, USER, PASSWORD, DB, TABLE 
from config    import ULTRASONIC_WATER_METER_LIST, LXC_SERIAL_NUMBER_LIST, CHOOSE_ONE_USB

from tools.flip           import flip
from tools.print_t        import print_t as print
from tools.time_lib       import current_time, current_date
from tools.serial_lib     import READ_COMMAND, to_select_command
from tools.serial_lib     import read_format, get_flow_rate, get_total_volume, get_return_serial_num
from tools.save_as_csv    import save_as_csv
from tools.check_internet import check_internet

from drivers.database import DBSetup

class LXCSetup():
    def __init__(self, tag, port, interval=0.0):
        self.name     = 'lxc'
        self.tag      =  tag
        self.port     =  port
        self.interval =  interval
        
        self.ser        =  None
        self.data       =  None
        self.use_db     =  None
        self.select_cmd = 'None'
        self.serial_num = 'None'
        self.location   = 'None'
        self.status     = 'GOOD'
        
        if not self.connect_db():
            print('error', '"__init__" -> An error occurred while setup the DB', self.tag)
            
        if not self.connect_serial(timeout=1):
            print('error', '__init__" -> An error occurred while setup the Serial', self.tag)

    def connect_db(self):
        if check_internet():
            if USE_DB:
                try:
                    self.db     = DBSetup(HOST, USER, PASSWORD, DB, TABLE)
                    self.use_db = True
                    return True
                
                except:
                    self.use_db = False
                    return 0
        else:
            if USE_DB:
                self.use_db = False
                print('warning', '"connect_db" -> Cannot connect to DB because there is no internet connection.', self.tag)
        
    def connect_serial(self, timeout):
        try:
            self.ser = Serial(port=self.port, baudrate=2400, parity='E', timeout=timeout)
            if not self.ser.is_open:
                self.ser.open()
        except:
            print('error', '"connect_serial" -> [ERROR_00] An error occurred while setup the serial port.', self.tag)
            self.status = 'ERROR_00'
            return 0
        return True
    
    def find_thread_start(self):
        thread = Thread(target=self.find_serial_num, daemon=True)
        thread.start()
        return thread
    
    def find_serial_num(self):
        if self.status == 'GOOD':
            for fliped_serial_num in flip(LXC_SERIAL_NUMBER_LIST):
                select_command = to_select_command(fliped_serial_num)
                try:
                    self.ser.write(select_command)
                    response = self.ser.read(1)
                except:
                    print('error', '"find_serial_num" -> [ERROR_01] An error occurred in the process of writing and reading.', self.tag)
                    self.status = 'ERROR_01'
                    break
                        
                if response == b'\xE5':
                    self.select_cmd = select_command
                    self.serial_num = flip(fliped_serial_num)
                    self.location   = ULTRASONIC_WATER_METER_LIST[self.serial_num]
                    print('success', f'"find_serial_num" -> Found {self.serial_num} ({self.location}).', self.tag)
                    self.status = 'GOOD'
                    break
                else:
                    continue
                
            if self.serial_num == None:
                print('error', '"find_serial_num" -> [ERROR_02] No connected LXC found.', self.tag)
                self.status = 'ERROR_02'
                            
    def select(self):
        try:
            self.ser.write(self.select_cmd)
            response = self.ser.read(1)
        except:
            print('error', '"select" -> [ERROR_03] An error occurred while selecting a serial number.', self.tag)
            self.status = 'ERROR_03'
            return 0
        
        if response == b'\xE5':
            self.status = 'GOOD'
            return True
        
        else: 
            print('error', '"select" -> [ERROR_04] Cant select because the response is not "E5".', self.tag)
            self.status = 'ERROR_04'
            return 0
        
    def read(self):
        try:
            self.ser.write(READ_COMMAND)
            read_data = self.ser.read(39)
            # format : b"h!!h\x08\xffr\x15\x13  \x00\x00\x02\x16\x00\x00\x00\x00\x04\x13\x00\x00\x00\x00\x05>\x00\x00\x00\x00\x04m\x17+\xbc'\xe9\x16"
        except:
            print('error', '"read" -> [ERROR_05] An error occurred while executing the Read command.', self.tag)
            self.status = 'ERROR_05'
            return 0
        if read_data[-1:] != b'\x16':
            print('error', '"read" -> [ERROR_06] Last data in read response is not "16".', self.tag)
            self.status = 'ERROR_06'
            return 0
        if read_data == b'':
            print('error', '"read" -> [ERROR_07] Read response is empty.', self.tag)
            self.status = 'ERROR_07'
            return 0
        if self.serial_num != get_return_serial_num(read_format(read_data, 7, 11)):
            print('error', '"read" -> [ERROR_08] Returned serial_number are different.', self.tag)
            self.status = 'ERROR_08'
            return 0
        try:
            self.data = {
                'time'         : current_time(),
                'serial_num'   : get_return_serial_num(read_format(read_data, 7, 11)),
                'flow_rate'    : get_flow_rate(read_format(read_data, 27, 31)),
                'total_volume' : get_total_volume(read_format(read_data, 21, 25))    }
        except:
            print('error', '"read" -> [ERROR_09] An error occurred while converting the data.', self.tag)
            self.status = 'ERROR_09'
            return 0
        
        return True
    
    def loop_thread_start(self):
        thread = Thread(target=self.loop, daemon=True)
        thread.start()
    
    def loop(self):
        error_stack = 0
        while self.status == 'GOOD':
            if error_stack > 50:
                break
            
            if not self.select():
                error_stack += 1
                continue
            
            for _ in range(10):
                sleep(self.interval)
                
                if not self.read():  
                    error_stack += 1
                    continue
                time         = self.data['time']
                serial_num   = self.data['serial_num']
                flow_rate    = self.data['flow_rate']
                total_volume = self.data['total_volume']
                
                if None in [time, serial_num, flow_rate, total_volume]:  
                    error_stack += 1
                    continue
                
                if USE_CSV_SAVE:
                    path    = f"{CSV_SAVE_PATH}/{current_date()}_{self.serial_num}"
                    data    = [ time,   serial_num,   flow_rate,   total_volume ]
                    columns = ['time', 'serial_num', 'flow_rate', 'total_volume']
                    save_as_csv(device=self.name, data=data, columns=columns, path=path)
                
                if self.use_db:
                    sql = f"INSERT INTO {self.db.table} (time, serial_num, flow_rate, total_volume) VALUES ('{time}', '{serial_num}', '{flow_rate}', '{total_volume}')"
                    self.db.send(sql)
                
                print('read', f'{time} | {serial_num:^12} | {flow_rate:11.6f} ???/h | {total_volume:11.6f} ???', self.tag)
                self.status = 'GOOD'
        
        print('error', '"loop" -> [ERROR_10] Exit the loop with a fatal error.')   
        self.status = 'ERROR_10'
        # To do : Send error message to db
        
        while True: 
            if True: 
                # If the condition is satisfied, the loop starts again.
                break        
        
        print('log', 'Restart the loop.')   
        self.status = 'GOOD'
        self.loop_thread_start()
        
                                   