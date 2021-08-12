import os
import pandas as pd

from config        import CSV_SAVE_PATH
from tools.print_t import print_t as print

def save_as_csv(device, data, columns, path):
    data_frame = pd.DataFrame([data], columns=columns)
    
    if path[-4:] != '.csv':
        path += '.csv'
    
    if not os.path.exists(path):
        try:
            data_frame.to_csv(path, index=False, mode='w', encoding='utf-8-sig')
        except FileNotFoundError:
            print('log', 'Create CSV_Files directory')
            os.system(f'sudo mkdir {CSV_SAVE_PATH}')
    else:
        data_frame.to_csv(path, index=False, mode='a', encoding='utf-8-sig', header=False)
