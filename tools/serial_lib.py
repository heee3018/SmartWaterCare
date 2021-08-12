from struct     import unpack
from binascii   import hexlify   as hex2str
from binascii   import unhexlify as str2hex
from tools.flip import flip
    
READ_COMMAND = str2hex('107BFD7816')

def crc(address):
    return ('%x' %sum(str2hex('73FD52' + address + 'FFFFFFFF')))[-2:]

def to_select_command(reversed_num):
    if type(reversed_num) == list:
        result = list()
        for address in reversed_num:
            result.append(str2hex('680B0B6873FD52' + address + 'FFFFFFFF' + crc(address) + '16'))
            
        return result
    
    else:
        return str2hex('680B0B6873FD52' + reversed_num + 'FFFFFFFF' + crc(reversed_num) + '16')
    
def read_format(hex_data, from_start, to_end):
    read_data = hex_data[from_start:to_end]
    read_data = hex2str(read_data)
    read_data = str(read_data)[2:-1]
    return read_data

def get_return_serial_num(str_data):
    retrun_serial_num = flip(str_data)
    return retrun_serial_num

def get_flow_rate(str_data):
    flow_rate = flip(str_data)
    flow_rate = str2hex(flow_rate)
    flow_rate = unpack('!f', flow_rate)[0]
    
    return flow_rate

def get_total_volume(str_data):
    total_volume = flip(str_data)
    total_volume = int(total_volume, 16) / 1000
    return total_volume

if __name__ == '__main__':
    select_command = str(hex2str(to_select_command(flip(input('Please enter your Serial number : ')))))[2:-1]
    
    for i in range(0, 34, 2):
        print(select_command[i:i+2], end=" ")
    