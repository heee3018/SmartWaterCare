from time      import sleep
from threading import Thread
from serial    import Serial, serialutil
from tools.print_t import print_t as print
from tools.check_internet import check_internet
from config    import SERIAL_NUMBER
from config    import USE_CSV_SAVE, CSV_SAVE_PATH
from config    import USE_DB, HOST, USER, PASSWORD, DB, TABLE 
from config    import LXC_SERIAL_NUMBER_LIST, CHOOSE_ONE_USB
from drivers.database import DBSetup
# from drivers.library  import current_time, current_date, save_as_csv, check_internet
# from drivers.library  import READ_COMMAND, flip, read_format, to_select_command
# from drivers.library  import get_flow_rate, get_total_volume, get_return_serial_num

class LXCSetup():
    def __init__(self, tag, port, interval=0.0):
        self.name       = 'lxc'
        self.tag        =  tag
        self.port       =  port
        self.interval   =  interval
        self.serial     =  None
        self.serial_num =  None
        self.select_cmd =  None
        self.data       =  None
        self.error_code = '00'
        
        if not self.connect_db():
            print('error', '"__init__" -> An error occurred while setup the DB', self.tag)
            
        if not self.connect_serial():
            print('error', '__init__" -> An error occurred while setup the Serial', self.tag)

    def connect_db(self):
        if check_internet():
            if USE_DB:
                try:
                    self.db = DBSetup(HOST, USER, PASSWORD, DB, TABLE)
                except:
                    return 0
        else:
            if USE_DB:
                print('warning', '"connect_db" -> Cannot connect to DB because there is no internet connection.', self.tag)
        return True

    def connect_serial(self):
        try:
            self.serial = Serial(port=self.port, baudrate=2400, parity='E', timeout=1)
            if not self.serial.is_open:
                self.serial.open()
        except:
            return 0
        return True
    
    def find_thread_start(self):
        thread = Thread(target=self.find_serial_num, daemon=True)
        thread.start()
    
    def find_serial_num(self):
        for fliped_serial_num in flip(LXC_SERIAL_NUMBER_LIST):
            select_command = to_select_command(fliped_serial_num)
            
            self.serial.write(select_command)
            response = self.serial.read(1)
                        
            if response == b'\xE5':
                self.select_cmd = select_command
                self.serial_num = flip(fliped_serial_num)
                print('success', f'"find_serial_num" -> Found {self.serial_num}.', self.tag)
                break
            if response == b'':
                print('error', '"find_serial_num" -> Empty response.', self.tag)
                continue
            else:
                continue
            
    def check(self):
        if not self.serial.is_open:
            print('error', f'"check" -> {self.port} The serial port is closed.', self.tag)
            return 0
        
        
        return True  
            
    def select(self):
        if self.select_cmd != None:
            self.serial.write(self.select_cmd)
            response = self.serial.read(1)
            
        if response != b'\xE5': 
            print('error', '"select" -> Cant select because the response is not "E5".', self.tag)
            return 0
        
        return True
    
    def read(self):
        try:
            self.serial.write(READ_COMMAND)
            read_data = self.serial.read(39)
            # format : b"h!!h\x08\xffr\x15\x13  \x00\x00\x02\x16\x00\x00\x00\x00\x04\x13\x00\x00\x00\x00\x05>\x00\x00\x00\x00\x04m\x17+\xbc'\xe9\x16"
        except:
            print('error', '"read" -> An error occurred while executing the Read command.', self.tag)
            return 0
        if read_data[-1:] != b'\x16':
            print('error', '"read" -> Last data in read response is not "16".', self.tag)
            return 0
        if read_data == b'':
            print('error', '"read" -> Read response is empty.', self.tag)
            return 0
        if self.serial_num != get_return_serial_num(read_format(read_data, 7, 11)):
            print('error', '"read" -> Returned serial_number are different.', self.tag)
            return 0
        try:
            self.data = {
                'time'         : current_time(),
                'serial_num'   : get_return_serial_num(read_format(read_data, 7, 11)),
                'flow_rate'    : get_flow_rate(read_format(read_data, 27, 31)),
                'total_volume' : get_total_volume(read_format(read_data, 21, 25))    }
        except:
            print('error', '"read" -> An error occurred while retrieving data.', self.tag)
            return 0
        
        return True
    
    def loop_thread_start(self):
        thread = Thread(target=self.loop, daemon=True)
        thread.start()
    
    def loop(self):
        READ_NUMBER_OF_ITERATIONS = 10
        
        while True:
            if not self.check(): 
                print('error', f'"loop" -> {self.port} The serial port is closed.', self.tag)
                continue
            if not self.select():
                print('error', f'"loop" -> Select error occurred.', self.tag)
                continue
            else:
                for _ in range(READ_NUMBER_OF_ITERATIONS):
                    if not self.read():
                        print('error', f'"loop" -> Read error occurred.', self.tag)
                        continue
                    
                    sleep(self.interval)   
                             
                    time         = self.data['time']
                    serial_num   = self.data['serial_num']
                    flow_rate    = self.data['flow_rate']
                    total_volume = self.data['total_volume']

                    if None in [time, serial_num, flow_rate, total_volume]:
                        print('error', f'"loop" -> Data contains the value none.', self.tag)
                        continue
                    
                    if USE_CSV_SAVE:
                        path    = f"csv_files/{current_date()}_{self.serial_num}"
                        data    = [ time,   serial_num,   flow_rate,   total_volume ]
                        columns = ['time', 'serial_num', 'flow_rate', 'total_volume']
                        save_as_csv(device=self.name, data=data, columns=columns, path=path)
                    # If None is present, it will not be sent to the db.
                    
                    if self.use_db:
                        sql = f"INSERT INTO {self.db.table} (time, serial_num, flow_rate, total_volume) VALUES ('{time}', '{serial_num}', '{flow_rate}', '{total_volume}')"
                        self.db.send(sql)
                    
                    print(f"{'[READ]':>10} {self.tag} - {time} | {serial_num:^12} | {flow_rate:11.6f} ㎥/h | {total_volume:11.6f} ㎥ |")
                                   
                                   
                                   
                                   
                                   
                                   
                                   
                                   
                                   
        
class LXC(object):
    def __init__(self, tag, port, interval):
        self.name     = 'lxc'
        self.tag      =  tag
        self.port     =  port
        self.interval =  interval
         
        self.state      = 'init'
        self.serial_num =  None
        self.select_cmd =  None
        self.data       =  {
            'time'         :  None,
            'serial_num'   :  None,
            'flow_rate'    :  None,
            'total_volume' :  None
        }
        
    def connect_port(self):
        for _ in range(5):
            try:
                self.ser = Serial(port=self.port, baudrate=2400, parity='E', timeout=1)
            except serialutil.SerialException as e:
                if 'Could not configure port' in str(e):
                    # print(f"{'[ERROR]':>10} {self.tag} - {self.port} Could not configure port")
                    pass
                elif 'could not open port' in str(e):
                    # print(f"{'[ERROR]':>10} {self.tag} - {self.port} could not open port")
                    pass
                else:
                    print(f">>{e}<<")
                continue
            except OSError:
                # print(f"{'[ERROR]':>10} {self.tag} - {self.port} Protocol error")
                continue
            
            if not self.ser.is_open:
                try:
                    self.ser.open()
                except:
                    # print(f"{'[ERROR]':>10} {self.tag} - {self.port} Could not open serial port.")
                    continue
            # print(f"{'[LOG]':>10} {self.tag} - Successfully opened the port")   
            break
        return True
    
    def search_serial_num(self):
        for _ in range(10):
            for fliped_serial_num in flip(LXC_SERIAL_NUMBER_LIST):
                select_command = to_select_command(fliped_serial_num)
                try:
                    self.ser.write(select_command)
                except:
                    # print(f"{'[ERROR]':>10} {self.tag} - {self.port} Failed to write Select command.")
                    self.state = 'select write error'
                    continue
                try:
                    response = self.ser.read(1)
                except:
                    # print(f"{'[ERROR]':>10} {self.tag} - {self.port} Failed to read Select command.")
                    self.state = 'select read error'
                    continue
                
                if response == b'\xE5':
                    self.state      = 'enabled'
                    self.select_cmd =  select_command
                    self.serial_num =  flip(fliped_serial_num)
                    break
                if response == b'':
                    self.state = 'empty response'
                    continue
                else:
                    self.state = 'disabled'
                    continue
            break
        
    def select_serial_num(self, serial_num):
        try:
            self.ser.write(to_select_command(flip(serial_num)))
        except:
            # print(f"{'[ERROR]':>10} {self.tag} - {self.port} Failed to write Select command.")
            self.state = 'error'
            return False
        try:
            response = self.ser.read(1)
        except:
            # print(f"{'[ERROR]':>10} {self.tag} - {self.port} Failed to read Select command.")
            self.state = 'error'
            return False
        
        if response == b'\xE5':
            self.state = 'enabled'
            return True
        else:
            self.state = 'disabled'
            return False
            
    def init(self):
        if not self.ser.is_open:
            print(f"{'[ERROR]':>10} {self.tag} - {self.port} The serial port is closed.")
            return False
        
        if self.serial_num == None    : return False
        if   self.state == 'init'     : return False
        elif self.state == 'enabled'  : pass
        elif self.state == 'disabled' : return False
        elif self.state == 'error' : return False
        return True
 
    def select(self):
        self.ser.write(self.select_cmd)
        if self.ser.read(1) != b'\xE5': 
            print(f"{'[ERROR]':>10} {self.tag} - Serial response is not E5.")
            return False
        
        return True
    
    def read(self):
        self.ser.write(READ_COMMAND)
        try:
            read_data = self.ser.read(39) 
        except serialutil.SerialException as e:
            if 'read failed' in str(e):
                print(f"{'[ERROR]':>10} {self.tag} - {self.port} Read failed : device reports readiness to read but returned no data")
                pass 
        # format : b"h!!h\x08\xffr\x15\x13  \x00\x00\x02\x16\x00\x00\x00\x00\x04\x13\x00\x00\x00\x00\x05>\x00\x00\x00\x00\x04m\x17+\xbc'\xe9\x16"
    
        if read_data[-1:] != b'\x16':
            print(f"{'[ERROR]':>10} {self.tag} - Invalid value.")
            return False
        if read_data == b'':
            print(f"{'[ERROR]':>10} {self.tag} - Empty response.")
            return False
        if self.serial_num != get_return_serial_num(read_format(read_data, 7, 11)):
            print(f"{'[ERROR]':>10} {self.tag} - 'serial_num' and 'return_serial_num' are different.")
            return False
        
        try:
            self.data = {
                'time'         : current_time(),
                'serial_num'   : get_return_serial_num(read_format(read_data, 7, 11)),
                'flow_rate'    : get_flow_rate(read_format(read_data, 27, 31)),
                'total_volume' : get_total_volume(read_format(read_data, 21, 25))
            }
        except:
            print(f"{'[ERROR]':>10} {self.tag} - Data get error.")
            return False
        
        return True
    
    
class Setup(LXC):
    def __init__(self, tag, port, interval=0):
        LXC.__init__(self, tag, port, interval)
        self.name = 'lxc'
        
    def connect_db(self):
        if USE_DB and check_internet():
            self.db = database.Setup(HOST, USER, PASSWORD, DB, TABLE)
            self.use_db = True
            # print(f"{'[LOG]':>10} {self.tag} - You have successfully connected to the db!")
        elif USE_DB and not check_internet():
            self.use_db = False
            print(f"{'[WARNING]':>10} {self.tag} - You must be connected to the internet to connect to the db.")
        else:
            self.use_db = False
            
    def start_search_thread(self):
        thread = Thread(target=self.search_serial_num, daemon=True)
        thread.start()
        return thread
    
    def start_read_thread(self):
        thread = Thread(target=self.read_thread, daemon=True)
        thread.start()
    
    def read_thread(self):
        while True:
            if not self.init(): 
                print(f"{'[ERROR]':>10} {self.tag} - Initialization error occurred")
            if not self.select():
                print(f"{'[ERROR]':>10} {self.tag} - Select error occurred")
            if not self.read():
                print(f"{'[ERROR]':>10} {self.tag} - Read error occurred") 
            else:
                sleep(self.interval)            
                time         = self.data['time']
                serial_num   = self.data['serial_num']
                flow_rate    = self.data['flow_rate']
                total_volume = self.data['total_volume']

                if None in [time, serial_num, flow_rate, total_volume]:
                    print(f"{'[ERROR]':>10} {self.tag} - Data contains the value none")
                
                if USE_CSV_SAVE:
                    path    = f"csv_files/{current_date()}_{self.serial_num}"
                    data    = [ time,   serial_num,   flow_rate,   total_volume ]
                    columns = ['time', 'serial_num', 'flow_rate', 'total_volume']
                    save_as_csv(device=self.name, data=data, columns=columns, path=path)
                # If None is present, it will not be sent to the db.
                
                if self.use_db:
                    sql = f"INSERT INTO {self.db.table} (time, serial_num, flow_rate, total_volume) VALUES ('{time}', '{serial_num}', '{flow_rate}', '{total_volume}')"
                    self.db.send(sql)
                
                print(f"{'[READ]':>10} {self.tag} - {time} | {serial_num:^12} | {flow_rate:11.6f} ㎥/h | {total_volume:11.6f} ㎥ |")
                                           
        # 여기서 다시 초기화
        # while True:
        #     if self.connect_port():
        #         self.search_serial_num()
        #         if self.state == 'enabled': 
        #             self.start_read_thread()
        #             break
                    
