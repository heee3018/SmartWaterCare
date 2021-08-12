def flip(serial_num):
    if type(serial_num) == list:
        result = list()
        
        for sn in serial_num:
            sn = sn[6:8] + sn[4:6] + sn[2:4] + sn[0:2]
            result.append(sn)
            
        return result
    
    else:
        return serial_num[6:8] + serial_num[4:6] + serial_num[2:4] + serial_num[0:2]
