import pymysql

class DBSetup():
    def __init__(self, host, user, password, db):
        self.db     = pymysql.connect(host=host, user=user, passwd=password, db=db, charset='utf8')
        self.cursor = self.db.cursor()
    
    def send_sql(self, sql):
        # sql : f"INSERT INTO {self.db.table} (time, serial_num, flow_rate, total_volume) VALUES ('{time}', '{serial_num}', '{flow_rate}', '{total_volume}')"
        self.cursor.execute(sql)
        self.db.commit()
        
    def send(self, table, field, values):
        # field  : "time, serial_num, flow_rate, total_volume"
        # values : [time, serial_num, flow_rate, total_volume]
        _values = []
        for val in values:
            _values.append('{'+val+'}')
        _values = str(_values)[1:-1]
        
        print(sql)
        sql = f"INSERT INTO {table} ({field}) VALUES ({_values})"
        # field  : "time, serial_num, flow_rate, total_volume"
        # values : "'{time}', '{serial_num}', '{flow_rate}', '{total_volume}'"
        self.cursor.execute(sql)
        self.db.commit()
        
    def close(self):
        self.db.close()