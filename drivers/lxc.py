from time      import sleep
from threading import Thread
from serial    import Serial, serialutil
from config    import USE_DB, USE_CSV_SAVE, CHOOSE_ONE_USB
from config    import FIND_COUNT, SERIAL_NUMBER_LIST
from config    import HOST, USER, PASSWORD, DB, TABLE 
from drivers   import database
from drivers.library import current_time, current_date, save_as_csv, check_internet
from drivers.library import READ_COMMAND, flip, read_format, to_select_command
from drivers.library import get_flow_rate, get_total_volume, get_return_serial_num

class LXC(object):
    def __init__(self, tag, port, interval):
        self.tag        = tag
        self.port       = port
        self.interval   = interval
         
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
            for fliped_serial_num in flip(SERIAL_NUMBER_LIST):
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
                    
                    
                    
                    
                    
                    
                    
                    

# class Setup():
#     def __init__(self, tag, port):
#         self.name             = 'lxc'
#         self.state            = 'init'
#         self.data             =  { }
#         self.tag              =  tag
#         self.serial_port      =  port
#         self.db               =  database.Setup(HOST, USER, PASSWORD, DB, TABLE)
#         self.error_cumulative = 0
        
#         self.connect_serial()

#     def connect_serial(self):
#         connect_serial_count = 5
#         while connect_serial_count > 0:
#             connect_serial_count -= 1
        
#             try:
#                 self.ser = Serial(port=self.serial_port, baudrate=2400, parity='E', timeout=1)
#                 if not self.ser.is_open:       
#                     self.ser.open()
                
#                 self.state = 'connected'
#                 print(f"{'[LOG]':>10} {self.tag} - Successfully opened the port")
#                 break
            
#             except serialutil.SerialException as e:
#                 if str(e)[:9] == '[Errno 2]':
#                     print(f"{'[ERROR]':>10} {self.tag} - Could not open port {self.tag}")
                    
#                 elif str(e)[:10] == '[Errno 72]':
#                     print(f"{'[ERROR]':>10} {self.tag} - {str(e)[10:]}")
                    
#                 self.state = 'disabled' 
#                 continue
            
#             except OSError:
#                 print(f"{'[ERROR]':>10} {self.tag} - Protocol error")
#                 self.state = 'disabled'
#                 continue
            
#     def start_search_thread(self):
#         thread = Thread(target=self.search_serial_num, daemon=True)
#         thread.start()
#         return thread
    
#     def search_serial_num(self): 
#         find_count = FIND_COUNT
#         while find_count > 0 and self.state == 'connected':
#             find_count -= 1
#             print(f"{'[LOG]':>10} {self.tag} - looking for Serial number that matches {self.tag}...")
#             for reversed_num in flip(SERIAL_NUMBER_LIST):
#                 select_command = to_select_command(reversed_num)
#                 self.ser.write(select_command)
                
#                 try:
#                     response = self.ser.read(1)
#                 except:
#                     continue

#                 if response == b'\xE5':
#                     print(f"{'[LOG]':>10} {self.tag} - {flip(reversed_num)} and {self.tag} were successfully matched !")
#                     self.data[flip(reversed_num)] = {
#                         'state'          : 'detected',
#                         'select'         :  select_command,
#                         'time'           :  current_time(),
#                         'serial_num'     :  None,
#                         'flow_rate'      :  None,
#                         'total_volume'   :  None
#                     }
                    
#                     if CHOOSE_ONE_USB:
#                         # If you are looking for only one
#                         self.data = {flip(reversed_num) : self.data[flip(reversed_num)]}
#                         break 
                
#                 else:
#                     self.data[flip(reversed_num)] = {
#                         'state'          : 'not detected',
#                         'select'         :  select_command,
#                         'time'           :  current_time(),
#                         'serial_num'     :  None,
#                         'flow_rate'      :  None,
#                         'total_volume'   :  None
#                     }

#             # If at least one 'state' in self.data is 'detected'
#             if 'detected' in [self.data[key]['state'] for key in list(self.data.keys())]:
#                 self.state = 'running'
#                 break 
            
#             else:
#                 print(f"{'[LOG]':>10} {self.tag} - Cannot find Serial Number for {self.tag}")
#                 self.state = 'not found'
#                 pass
                
#     def start_read_thread(self):
#         if self.state == 'running':
#             thread = Thread(target=self.read_data, daemon=True)
#             thread.start()
    
#     def read_data(self):
#         while True:
#             for key in list(self.data.keys()):
#                 select_command = self.data[key]['select']
#                 self.ser.write(select_command)
                
#                 if self.ser.read(1) == b'\xE5':
#                     repeat = 10
#                     while repeat > 0:
#                         repeat -= 1
                        
#                         self.ser.write(READ_COMMAND)
#                         read_data = self.ser.read(39)
                        
#                         if read_data == b'':
#                             print(f"{'[ERROR]':>10} {self.tag} - Eempty response")
#                             self.error_cumulative += 1
#                             break
                        
#                         try:
#                             time         = current_time()
#                             serial_num   = get_return_serial_num(read_format(read_data, 7, 11))
#                             flow_rate    = get_flow_rate(read_format(read_data, 27, 31))
#                             total_volume = get_total_volume(read_format(read_data, 21, 25))
#                         except:
#                             print(f"{'[ERROR]':>10} {self.tag} - Eempty response")
#                             self.error_cumulative += 1
#                             break
                        
#                         # Update self.data
#                         if key == serial_num:
#                             self.data[key] = {
#                                 'state'          : 'runnuing',
#                                 'select'         :  select_command,
#                                 'time'           :  current_time(),
#                                 'serial_num'     :  key,
#                                 'flow_rate'      :  flow_rate,
#                                 'total_volume'   :  total_volume
#                             }
                        
#                         # Save as csv
#                         if USE_CSV_SAVE:
#                             path = f"csv/{current_date()}_{key}"
#                             data = [time, serial_num, flow_rate, total_volume]
#                             columns = ['time', 'serial_num', 'flow_rate', 'total_volume']
#                             save_as_csv(device=self.name, data=data, columns=columnspath=path)
                        
#                         # Send to db
#                         if USE_DB:
#                             self.db.send(f"INSERT INTO {self.db.table} (time, serial_num, flow_rate, total_volume) VALUES ('{time}', '{serial_num}', '{flow_rate}', '{total_volume}')")
                        
#                         print(f"{'[READ]':>10} {self.tag} - {time} | {serial_num:^12} | {flow_rate:11.6f} ㎥/h | {total_volume:11.6f} ㎥ |")
                                   
#                 else:
#                     self.error_cumulative += 1
                
#             if self.error_cumulative >= 10:
#                 print(f"{'[ERROR]':>10} {self.tag} - Error accumulates and restarts..")
#                 self.connect_serial()
#                 search_thread = self.start_search_thread()
#                 search_thread.join()
#                 self.start_read_thread()
#                 break
