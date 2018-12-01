import sqlite3
import threading
import os
import time
import pickle
from datetime import datetime

#for file details
list_lock = threading.Semaphore(1)
#for log file
log_lock = threading.Semaphore(1)
#for user login 
sem = threading.Semaphore(1)

def getUserList(c,data):
	#accquire lock to reead from db
	sem.acquire()
	conn = sqlite3.connect('db\\login.db')
	c = conn.cursor()
	c.execute("SELECT * FROM users")
	rows = c.fetchall()
	print("list of registered users")
	print(rows)
	#close connection with db and lock relese
	conn.close()
	sem.release()
	return rows

def listFiles(c,currentUser):
	print("list files for ", currentUser)
	#accwire lock and get list of files of current user
	list_lock.acquire()
	conn_file = sqlite3.connect('db\\file.db')
	cur = conn_file.cursor()
	cur.execute("SELECT * FROM file WHERE user=(?)", (currentUser,))
	rows = cur.fetchall()
	conn_file.commit()
	conn_file.close()
	list_lock.release()
	#release lock and end connection with db file
	print("list acquired")
	files = str(len(list(rows)))
	print(rows)
	c.send(files.encode("ascii"))
	if int(files) >0:
		row = pickle.dumps(rows)
		time.sleep(1)
		c.send(row)
	print("send details to client")
	return rows

#for registering new user
def regUser(c,data):
	rows = getUserList(c,data)
	x = 1
	#check if user already present
	for row in rows:
		if row[0] == data[1]:
			print("user already exists")
			c.send("unsucessfull".encode('ascii'))
			return 0
	# send ACK to client
	c.send("sucessfull".encode('ascii'))
	#update in db file
	sem.acquire()
	conn = sqlite3.connect('db\\login.db')
	c = conn.cursor()
	c.execute("INSERT INTO users VALUES (?, ?);", (data[1], data[2]))
	conn.commit()
	conn.close()
	sem.release()
	#create dir for user
	dirName = 'root/' + data[1]
	try:
		#create directory for created user
	    os.mkdir(dirName)
	    print("Directory for" + data[1]+ "sucessfully created ") 
	except FileExistsError:
		print("Error creating directory for" + data[1])
	print("new user created")
	return 1

#to login user
def loginUser(c,data):
	print("login request recieved")
	print("checking user present on not")
	#get list of registered users with their passwords
	rows = getUserList(c,data)
	x = 0
	#check username and password
	for row in rows:
		if row[0] == data[1]:
			if row[1] == data[2]:
				print("login sucessfull")
				c.send("sucessfull".encode('ascii'))
				return 1
	# send uncessfull if user id or password dont match
	if x == 0:
		c.send("unsucessfull".encode('ascii'))
		return 0

#get file from user
def getFileFromUser(c,data,addr):
	#path where file is to be saved
	file = "root\\"+ data[1] +"\\" + data[2]
	#create and open new file
	with open(file, 'wb+') as f:
	    print ('file opened')
	    while True:
	        print('receiving data...')
	        content = c.recv(10240)
	        print('data=%s', (content))
	        if str(content) == "b'OVER'":
	        	f.close()
	        	print( 'file succesfully recieved')
	        	break
	        else:
	        	f.write(content)
	#update activity of user in db
	print("updating in db")
	log_lock.acquire()
	conn_file = sqlite3.connect('db\\log.db')
	cur = conn_file.cursor()
	print("entering")
	cur.execute("INSERT INTO log VALUES (?, ?,?,?,?);", (data[1], "upload", data[2],addr[0], datetime.now()))
	conn_file.commit()
	conn_file.close()
	log_lock.release()
	print("here")
	#update files info of user
	list_lock.acquire()
	conn_file = sqlite3.connect('db\\file.db')
	cur = conn_file.cursor()
	cur.execute("INSERT INTO file VALUES (?, ?,?,?);", (data[2],  data[1], data[1],datetime.now()))
	conn_file.commit()
	conn_file.close()
	list_lock.release()
	print('Successfully updated in file directory')
	print("done")


def showLog(c,data):
	print("showing log")
	currentUser = data[-1]
	log_lock.acquire()
	conn_file = sqlite3.connect('db\\log.db')
	cur = conn_file.cursor()
	if data[1]=="all":
		cur.execute("SELECT * FROM log")
	else:
		cur.execute("SELECT * FROM log WHERE username=(?)", (currentUser,))
	rows = cur.fetchall()
	conn_file.close()
	log_lock.release()
	print("list acquire")
	#print(rows)
	l = str(len(list(rows)))
	print(l)
	print(rows)
	c.send(l.encode("ascii"))
	#for row in rows:
	row = pickle.dumps(rows)
	time.sleep(1)
	c.send(row)
	print("send details")


def delFile(c,data,addr):
	if data[1] == "yes":
		#remove file from user directory
		filePath = "root\\" + data[2] + "\\" + data[-1]
		os.remove(filePath)
	try:
		#uodate deletion indb
		log_lock.acquire()
		conn_file = sqlite3.connect('db\\log.db')
		cur = conn_file.cursor()
		print("entering")
		cur.execute("INSERT INTO log VALUES (?, ?,?,?,?);", (data[2], "delete", data[-1],addr[0], datetime.now()))
		conn_file.commit()
		conn_file.close()
		log_lock.release()
		
		#update files info of user
		list_lock.acquire()
		conn_file = sqlite3.connect('db\\file.db')
		cur = conn_file.cursor()
		if data[1] == "yes":
			cur.execute("DELETE FROM file WHERE filename=(?)", (data[-1],))
		else:
			cur.execute("DELETE FROM file WHERE (filename,user)=(?,?)", (data[-1],data[2]))
		conn_file.commit()
		conn_file.close()
		list_lock.release()
	except:
		#send ACk
		c.send("unsucessfull".encode('ascii'))
		print('something went wrong while deleting the file')
		return 0
	c.send("sucessfull".encode('ascii'))
	print('Successfully updated in file directory')

def giveFileToUser(c,data,addr):
	#path of file which is to downloade dby user
	filePath = "root\\" + data[2] +"\\" + data[3]
	f = open(filePath,'rb')
	l = f.read(10240)
	x =1
	try:
	    while (l):
	        c.send(l)
	        #print('Sent ',repr(l))
	        l = f.read(10240)
	    if not l:
	        time.sleep(1)
	        f.close()
	        print("file successfully uploaded")
	        c.send("OVER".encode("ascii"))
	except:
		#message to say end of file
		c.send("OVER".encode("ascii"))
		c.send("unsucessfull".encode('ascii'))
		print("some error occurred while sending file to user")
		x = 0
	if x == 1:
		#send Ack and uodate log in db
		c.send("sucessfull".encode('ascii'))
		log_lock.acquire()
		conn_file = sqlite3.connect('db\\log.db')
		cur = conn_file.cursor()
		print("entering")
		cur.execute("INSERT INTO log VALUES (?, ?,?,?,?);", (data[1], "download", data[-1],addr[0], datetime.now()))
		conn_file.commit()
		conn_file.close()
		log_lock.release()

def shareFiles(c,data,addr):
	#update activity of user in db
	try:
		log_lock.acquire()
		conn_file = sqlite3.connect('db\\log.db')
		cur = conn_file.cursor()
		print("entering")
		cur.execute("INSERT INTO log VALUES (?, ?,?,?,?);", (data[1], "share", data[-1],addr[0], datetime.now()))
		conn_file.commit()
		conn_file.close()
		log_lock.release()
		
		#update files info of user
		list_lock.acquire()
		conn_file = sqlite3.connect('db\\file.db')
		cur = conn_file.cursor()
		cur.execute("INSERT INTO file VALUES (?, ?,?,?);", (data[-1],  data[2], data[1],datetime.now()))
		conn_file.commit()
		conn_file.close()
		list_lock.release()
		c.send("sucessfull".encode('ascii'))
		print('Successfully shared file')
	except:
		c.send("unsucessfull".encode('ascii'))
		print('some error occured while sharing file')

def openFile(c,data):
	#path of file to be opened
	filePath = "root\\" + data[1] + "\\" + data[-1]
	try:
		os.startfile(filePath)
	except:
		#send ACK
		c.send("unsucessfull".encode('ascii'))
		print('some error occured while opening file')
	#send ACK
	c.send("sucessfull".encode('ascii'))
	print('file opened succesfully')