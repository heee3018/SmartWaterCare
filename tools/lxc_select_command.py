from library   import flip, to_select_command
from binascii  import hexlify as hex2str

if __name__ == '__main__':
    address = input('Type the address : ')
    select_command = str(hex2str(to_select_command(flip(address))))[2:-1]
    
    for i in range(0, 34, 2):
        print(select_command[i:i+2], end=" ")
    