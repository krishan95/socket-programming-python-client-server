import sqlite3

conn = sqlite3.connect('db\\login.db')
c= sqlite3.connect('db\\log.db')
conn = conn.cursor()
c = c.cursor()
c2 = sqlite3.connect('db\\file.db')
c2 = c2.cursor()

conn.execute('''CREATE TABLE users (
    username varchar(255) NOT NULL,
    password varchar(255) NOT NULL,
    PRIMARY KEY (username)
	)''')

c.execute('''CREATE TABLE log (
    username varchar(255) NOT NULL,
    action varchar(255),
    file varchar(255),
    ip varchar(255),
    TS DATETIME DEFAULT NULL
	)''')

c2.execute('''CREATE TABLE file (
    filename varchar(255) NOT NULL,
    user varchar(255),
    owner varchar(255),
    TS DATETIME DEFAULT NULL
	)''')
