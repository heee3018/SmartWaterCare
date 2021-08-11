import pymysql

class DBSetup():
    def __init__(self, host, user, password, db, table):
        self.db = pymysql.connect(host=host, user=user, passwd=password, db=db, charset='utf8')
        self.cursor = db.cursor()
    
    def send_sql(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        
    def close(self):
        self.db.close()