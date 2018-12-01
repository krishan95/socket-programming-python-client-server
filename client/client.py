# Import socket module 
import socket 
import sqlite3
import caction
from caction import *

#start options
def start(s):
    print("----------------------------")
    print("1. login")
    print("2.signup")
    print("3.exit")
    try:
        i = int(input())
    except:
        print("invalid input")
        print("please try again")
        start(s)
    if i == 1 or i == 2:
        caction.login_signup(s,i)
    elif i == 3:
        details = "exit" + " " + "exit" 
        s.send(details.encode('ascii'))
    else:
        print("invalid input")
        print("please try again")
        start(s)

def Main(): 
    # host and port for connection 
    host = '127.0.0.1'
    port = 81
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # connect to server
    s.connect((host,port)) 
    start(s)
    s.close() 
  
if __name__ == '__main__': 
    Main() 
