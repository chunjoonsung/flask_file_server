import sqlite3

user_table = '''
CREATE TABLE "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "username" VARCHAR(80) NOT NULL UNIQUE,
    "password" VARCHAR(80) NULL,
    "admin" INTEGER NULL
);
'''

class Sqlite():
    def __init__(self,dbfile):
        self.conn = sqlite3.connect(dbfile)
    def execute(self,query):
        self.conn.cursor().execute(query)
    def select(self,query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.close()

def create_table(username,password,admin=0):
    sql = Sqlite("user.db")
    sql.execute(user_table)
    sql.execute(f"INSERT INTO user (username, password, admin) VALUES ('{username}','{password}','{admin}')")
    sql.commit()
    
def create_user(username,password,admin=0):
    sql = Sqlite("user.db")
    sql.execute(f"INSERT INTO user (username, password, admin) VALUES ('{username}','{password}','{admin}')")
    sql.commit()
    
def query(username,password):
    sql = Sqlite("user.db")
    rows = sql.select(f"SELECT username, password, admin FROM user WHERE username='{username}'")
    print('rows',rows)
    if rows:
        for row in rows:
            print(row)
            print(row[0],row[1],row[2],type(row[2]))
            if row[1] == password:
                return row[2]
