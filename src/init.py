import sqlite3

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

user_table = '''
CREATE TABLE "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "username" VARCHAR(80) NOT NULL UNIQUE,
    "password" VARCHAR(80) NULL,
    "admin" INTEGER NULL
);
'''
    
if __name__ == "__main__":
    sql = Sqlite("user.db")
    sql.execute(user_table)
    sql.execute("INSERT INTO user (username, password, admin) VALUES ('psgam','psgam72','0')")
    sql.execute("INSERT INTO user (username, password, admin) VALUES ('pub','user1234','0')")
    sql.execute("INSERT INTO user (username, password, admin) VALUES ('admin','nimda4321','1')")
    sql.commit()
    rows = sql.select(f"SELECT username, password FROM user")
    for row in rows:
        print(row)

    
    
    
