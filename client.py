import socket
import time
import threading
c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def client_thread(c_socket,client_address,query1):
    c_socket.send(query1.encode())
    print("Data sent:" + query1.split()[0] )
    time.sleep(12)

c_socket_not_repeat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 1425
client_address1 = (host,port)
# c_socket_not_repeat.bind((host,port))
c_socket_not_repeat.connect((host,9999))
n = 2
BUFFER = 1024
for i in range (1,n+1):
    
    if i <=n/2:
        c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '127.0.0.'+str(i)
        port = 5000+i
        client_address = (host,port)
        c_socket.bind((host,port))
        c_socket.connect((host,9999))
        query1 = "THH http://index{key}.html HTTP/1.3\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n".format(key = str(i))
        t=threading.Thread(target=client_thread, args= (c_socket, client_address,query1,))
        t.start()
        messge = c_socket.recv(1048)
        print(messge)
#         time.sleep(5)
    else:
    
        query1 = "THHHH /index3.html HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n"
        c_socket_not_repeat.send(query1.encode())
        print("Data sent:" + query1.split()[0])         
#         time.sleep(5)
        messge = c_socket_not_repeat.recv(1048)
        print(messge)
    time.sleep(.2)


