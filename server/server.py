import socket 
import sqlite3
from saction import *
from _thread import *
import threading 

# thread fuction 
def threaded(c,addr): 
    # data received from client
    while True:
        data = c.recv(10240)
        data = str(data).split(" ")
        data[0] = data[0][2:]
        data[-1]=data[-1][:-1]
        print("request recieved for",data[0])
        if data[0] == "": 
            print('invalid input') 
        elif data[0] == "login":
            loginUser(c,data)
        elif data[0] == "exit":
            print("conecction ended with client" ,addr)
            break
        elif data[0] == "log":
            showLog(c,data)
        elif data[0] == "down":
            giveFileToUser(c,data,addr)
        elif data[0] == "del":
            delFile(c,data,addr)
        elif data[0] == "reg":
            regUser(c,data)
        elif data[0] == "list":
            listFiles(c,data[1])
        elif data[0] == "share":
            shareFiles(c,data,addr)
        elif data[0] == "upload":
            getFileFromUser(c,data,addr)
        elif data[0] == "open":
            openFile(c,data)
        else:
            print("unknown comand sent by client")
            break 
    c.close()


def Main(): 
    host = "" 
    port = 81
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port)) 
    print("socket binded to post", port) 
    # listening through soclet 
    s.listen(5)
    print("server is  listening") 
    while True: 
        # establish connection with client 
        c, addr = s.accept()
        print('Connected to :', addr[0], ':', addr[1]) 
        # Start a new thread 
        start_new_thread(threaded, (c,addr)) 
    s.close()
  
if __name__ == '__main__': 
    Main() 
