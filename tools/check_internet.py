import http.client as httplib

def check_internet(url='www.google.com', timeout=3):
    conn = httplib.HTTPConnection(url, timeout=timeout)
    try:
        conn.request('HEAD', '/')
        conn.close()
        return True
    except:
        return False
    
if __name__ == '__main__':
    if check_internet():
        print('Connected to the internet.')
    else:
        print('No internet connection')