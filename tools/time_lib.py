import os 
from datetime import datetime

def current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # format : 2020-05-04 10:18:32.926

def current_date():
    return datetime.now().strftime('%Y_%m_%d')

def time_sync():
    os.popen('sudo ntpdate -u 3.kr.pool.ntp.org')
    
def time_format(seconds: int):
    if seconds is not None:
        seconds = int(seconds)
        d = seconds // (3600 * 24)
        h = seconds // 3600 % 24
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        if d > 0:
            return '{:02d}D {:02d}H {:02d}m {:02d}s'.format(d, h, m, s)
        elif h > 0:
            return '{:02d}H {:02d}m {:02d}s'.format(h, m, s)
        elif m > 0:
            return '{:02d}m {:02d}s'.format(m, s)
        elif s > 0:
            return '{:02d}s'.format(s)
    return '-'

if __name__ == '__main__':
    print(time_format(87444))