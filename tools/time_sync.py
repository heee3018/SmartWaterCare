import os 

def time_sync():
    os.system('sudo ntpdate -u 3.kr.pool.ntp.org')