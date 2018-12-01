from client import *
import client
from prettytable import PrettyTable
import getpass
import pickle
import os
import time

def login_signup(s,i):
    print("enter details ->")
    userName = input("User name: ")
    password = getpass.getpass()
    #for login
    if i == 1:
        details = "login" +" " + userName + " " + password
        print("waiting to be logged in")
        s.send(details.encode('ascii'))
        st = str(s.recv(120))
        st = st[2:-1]
        if st == "sucessfull":
            print("login sucessful")
            action(s,userName)
        else:
            print("no such user")
            client.start(s)
    #for signup
    elif i == 2:
        details = "reg" +" " + userName + " " + password
        print("creating account")
        s.send(details.encode('ascii'))
        st = str(s.recv(120))
        st = st[2:-1]
        if str(st)== "sucessfull":
            print("register sucessful")
            print("-------------------------")
            print("enter details to log in")
            print("-------------------------")
            login_signup(s,1)

        else:
            print("user already exists, try picking another user name ")
            client.start(s)

#print data in form of table            
def printTab(arr,islogData,isFileList):
    if isFileList == "yes":
        t = PrettyTable(['Filename','Shared by another user','last modified'])
    elif islogData == "yes":
        t = PrettyTable(['User','action','file name','ip address','data/time'])
    for a in arr:
        if isFileList=="yes":
            if a[1] == a[2]:
                x = "no"
            else:
                x = "yes"
            t.add_row([a[0],x,a[3]])
        else:
            t.add_row(list(a))
    print(t)



#list all the files of a perticular user
#i represent whether to list files or show log
# j represent whether it tje final call or its ouput is to be used futhur
def printLog_File(s,userName,i,j):
    #list files of current user
    arr= []
    if i==1:
        message = "list" + " " + userName
        #s.send(message.encode("ascii"))
        s.send(message.encode("ascii"))
    else:
        print("1.show log for all users")
        print("2.show logs for current users")
        print("[press 0 to go back]")
        try:
            k = int(input())
        except:
            print("invalid choice")
            print("going back to home page")
            action(s,userName)
            return 0
        if k == 1:
            message = "log" + " " + "all" + " "+ userName
            s.send(message.encode("ascii"))
        elif k ==2:
            message = "log" + " " + "current" + " "+ userName
            s.send(message.encode("ascii"))
        else:
            print("invalid choice")
            print("going back to home page")
            action(s,userName)
            return 0
    #no of entries to recieve
    try:
        fileCount = (s.recv(10240))
        fileCount = str(fileCount)
        fileCount = int(fileCount[2:-1])
        print("no of enteries = ",fileCount)
    except:
        print("oops something went wrong")
        print("disconnecting connection")
        details = "exit" + " " + "exit" 
        s.send(details.encode('ascii'))
        time.sleep(.500)
        s.close()
        exit()
    if fileCount ==0:
        if i==1:
            print("no files to diplay")
        else:
            print("no logs to display")
    else:
            arr = pickle.loads(s.recv(10240))
            #for a in arr:
            if i ==1:
                printTab(arr,"no","yes",)
                #print(a[0])
            else:
                printTab(arr,"yes","no")
                #print(a)
    if j !=1:
        print("[press enter key to go back] ")
        input()
        action(s,userName)
        
    else:
        return arr


#action after login
def action(s,userName):
    print("----------------------------------")
    print("1.list files")
    print("2.upload file")
    print("3.download file")
    print("4.delete file")
    print("5.share file")
    print("6.show log")
    print("7.open file")
    print("8.sign out")
    print("9.clear screen")
    print("----------------------------------")
    print("enter choice:")
    try:
        i = int(input())
    except:
        print("invalid choice, try again")
        action(s,userName)        
    if i ==1 or i==6:
        printLog_File(s,userName,i,0)
    elif i==2:
        uploadFile(s,userName)
    elif i == 3:
        downloadFile(s,userName)
    elif i ==4:
        delete(s,userName)
    elif i==5:
        shareFile(s,userName)
    elif i==7:
        openFile(s,userName)
    elif i==8:
        print("exiting...")
        details = "exit" + " " + "exit" 
        s.send(details.encode('ascii'))
    elif i==9:
        os.system('cls')
        action(s,userName)
    else:
        print("invalid choice, try again")
        action(s,userName)

def uploadFile(s,userName):
    print("enter file location")
    file = input()
    #to get file name
    filename = file.split("\\")
    message = "upload" + " " + userName + " " + filename[-1]
    #check if file is present on given location or not
    exists = os.path.isfile(file)
    if exists == True: 
        try:
            f = open(file,'rb')
            l = f.read(10240)
        except:
            print("invalid file")
        s.send(message.encode("ascii"))
        time.sleep(.500)
        while (l):
            s.send(l)
            print("sending data")
            #print('Sent ',repr(l))
            l = f.read(10240)
        if not l:
            time.sleep(1)
            f.close()
            print("file successfully uploaded")
            s.send("OVER".encode("ascii"))
            action(s,userName)
    else:
        print("no such file exists")
        print("going back to home page")
        action(s,userName)

def delete(s,userName):
    print("enter file you want to delete")
    arr = printLog_File(s,userName,1,1)
    f = input()
    x,isOwner = 0,"no"
    for a in arr:
        if a[0] == f and a[1]==userName:
            x = 1
            #check whether current user is owner or file was shared with it
            if a[2] == userName:
                isOwner="yes"
                break
    if x == 0:
        print("incorrect file name")
        print("going to home page")
        action(s,userName)
    else:
        message = "del" + " " + isOwner + " " +  userName + " " + f  
        #send comand to server
        s.send(message.encode("ascii"))
        #recieve ACk from server
        st = str(s.recv(10240))
        st = st[2:-1]
        if st == "sucessfull":
            print("delete sucessful")
        else:
            print("some problem ocuured while deleteting...Please try again after some time")
        action(s,userName)

def downloadFile(s,userName):
    print("enter file you want to download")
    #get list of file present
    arr = printLog_File(s,userName,1,1)
    file = ("a",)
    #if no file present
    if len(arr) == 0:
        print("no file present for downloading")
        print("upload any file or ask your friend to share file for downloading")
        print("press enter to continue")
        input()
        action(s,userName)
    else:
        f = input()
        x= 0
        #check if given file name is correct
        for a in arr:
            if a[0] == f and a[1]==userName:
                x = 1
                file = a
                break
        if x == 0:
            print("incorrect file name")
            print("going to home page")
            action(s,userName)
        else:
            #send comand to server
            message = "down" + " " + userName + " "+ file[2] + " " +  f 
            s.send(message.encode("ascii"))
            file = f
        #get file from server
        with open(file, 'wb+') as f:
            print ('file opened')
            while True:
                print('receiving data...')
                content = s.recv(10240)
                #print('data=%s', (content))
                if str(content) == "b'OVER'":
                    f.close()
                    #print( 'file succesfully downloaded')
                    break
                else:
                    f.write(content)
            #get ACK from server
            st = str(s.recv(102))
            st = st[2:-1]
            if st == "sucessfull":
                print("download sucessful")
            else:
                print("some problem ocuured while downloading...Please try again after some time")
            action(s,userName)

def shareFile(s,userName):
    print("select file to share")
    arr = printLog_File(s,userName,1,1)
    f = input()
    x,isOwner = 0,"no"
    for a in arr:
        if a[0] == f and a[1]==userName:
            x = 1
            #check whether current user is owner or file was shared with it
            if a[2] == userName:
                isOwner="yes"
                break
    #incorrect file name
    if x==0:
        print("incorrect file name")
        print("going back to home page")
        action(s,userName)
    else:
        if isOwner == "no":
            print("you don't have permission to share this file")
            print("you can only share files you own")
            action(s,userName)
        
        else:
            print("enter name of user, you want to share file with")
            shareUser = input()
            #check if user to which file with itself
            if shareUser == userName:
                print("you can't share file with yourself")
                print("going to home page")
                action(s,userName)
            #send comand to server
            message = "share" + " " + userName + " " +shareUser + " " +  f
            s.send(message.encode("ascii"))
            #recieve ACK
            st = str(s.recv(102))
            st = st[2:-1]
            if st == "sucessfull":
                print("file has been succesfully shared")
            else:
                print("some problem ocuured while sharing...Please try again after some time")
            action(s,userName)        

def openFile(s,userName):
    print("enter file you want to open")
    arr = printLog_File(s,userName,1,1)
    f = input()
    x,isOwner = 0,"no"
    for a in arr:
        if a[0] == f and a[1]==userName:
            x = 1
            owner = a[2]
    #check file to be opened is given correctly or not
    if x == 0:
        print("incorrect file name")
        print("going to home page")
        action(s,userName)
    else:
        #send comand to server
        message = "open" + " " + owner + " " +  userName + " " + f  
        s.send(message.encode("ascii"))

        #recieve ACK
        st = str(s.recv(102))
        st = st[2:-1]
        if st == "sucessfull":
            print("file opened sucessful")
        else:
            print("some problem ocuured while opening...Please try again after some time")
        action(s,userName)