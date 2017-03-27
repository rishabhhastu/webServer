import socket 
import os
import time
import threading 
import configparser
import sys
import re    

def ConfigSectionMap(section):                                                      #Creates dictionary for all the ws.conf entries
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def send_data(header , status_code , to_send , file_present, client):               #sends data to the client
    try:
        client.send(header.encode())
        if file_present == 1:                                                       #checks if the file was present and sends the appropriate message
            client.send(to_send)
        else:
            client.send(to_send.encode())
    except Exception as e:
        print("Error: " + str(e))
        
def check_occurence(list1 , string):                                                #Checks if the unwanted symbols are present in the URL
    value = 0 
    for c in string:
        for l in list1:
            if c == l:
                value = 1       
    return value
        
def header_format( keep_alive , current_date , filesize, status_code, content_type, request_version):        # Returns the header for the according to status_code
    header = ''
    if status_code == 200:
        header += '{version} 200 OK\n'.format(version = request_version) 
    elif status_code == 404:
        header += '{version} 404 NOT FOUND\n\n'.format(version = request_version)
    elif status_code == 400:
        header += '{version} 400 Bad Request\n\n'.format(version = request_version)    
    elif status_code == 501:
        header += '{version} 501 Not Implemented\n\n'.format(version = request_version)
    elif status_code ==500:
        header += '{version} 500 Internal Server Error\n\n'.format(version = request_version)
    if status_code != 200:
        return header
    header += 'Connection: Keep-alive\n' if keep_alive == 1 else 'Connection: Close\n'
    header += 'Date: '+current_date+'\n'
    header += 'Content-Type: '+ content_type + '\n'
    header += 'Content-Length: ' + str(filesize)+ '\n\n'
    return header

def server_thread(client,client_address):                                                   #Thread Function of the server
    print('*'*25 + 'A New Thread'+'*'*50)
    print('TIME AT START OF THREAD:' + str(time.strftime("%H:%M:%S",time.localtime())))
    print('Name Of Thread: ' + str(threading.current_thread()))
    t=time.clock()                                                                          #Starts the clock for the counting the time thread is active
    persistent = 1
    print("Entered While Loop of Thread: ==" + str(threading.current_thread()))
    while persistent == 1:
        try:
            file_present = 0
            filesize = 0
            keep_alive = 0
            status_code = 0
            content_type = ''
            reason =''
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()) 
            index_file_present = 0
            print('Waiting from client' + str(client_address[1]))
            data_encoded = client.recv(BUFFER)                                              #receives the request from the respective clients
            if data_encoded == b'':
                print('CAptured Blank' + str(threading.current_thread()))
                
            data_decoded = data_encoded.decode('utf-8').split('\n')
            http_command = data_decoded[0].split()
            request_method = http_command[0]
            if request_method not in ['GET' , 'POST' , 'HEAD']:                             #Checks if the Requested header is Valid, if not, sends a BAD Request                            
                print('BAD METHOD')
                reason = 'Invalid Method'
                status_code = 400     
                        
            request_URL = http_command[1]
            if request_URL == '/':                                                          #Handles the server if the user enters just '/' for root directory
                for i in list_directory_index:
                    filename = document_root + i  
                    if os.path.isfile(filename):
                        index_file_present = 1
                        request_URL = i
                        break
            
            request_version = http_command[2]
            if request_version not in ('HTTP/1.1' , 'HTTP/1.0'):
                reason = 'Invalid HTTP-Version'
                status_code = 400
                
            if index_file_present !=1 and request_URL == '/':
                print('filepresent ' + str(file_present))                                   #For the 500 not implemented status code
                status_code = 500
                to_send = '<html><body>'+ str(status_code)+ ' Internal Server Error: cannot allocate memory</body></html>'
                header = header_format(keep_alive, current_date, filesize , status_code, content_type,request_version)
                send_data(header, status_code, to_send, file_present, client)
                break
            
            extension = '.'+request_URL.split('.')[1]
            
            if extension not in list_valid_extensions:                                          #Used to check if the extension is valid or not. If not, then returns 501 error
                status_code = 501
                to_send = '<html><body>'+ str(status_code)+ ' Not Implemented' + '</body></html>'
            else:
                content_type = dict_content[extension]
                
            list1 = ['*',':','&','%','#']                                                           
            value = check_occurence(list1, request_URL)                                     #Calls the function to check for unwanted characters
            if value == 1:
                status_code = 400
                reason = 'Invalid URL'
        
            if request_method == 'POST':                                                    #Implementing POST
                list_post = data_encoded.decode('utf-8').split(',')
                for i in list_post:
                    value = re.findall(r'nm=(.*)', i)                                           #Searches for the value put by the user in textbox
                    if  value :
                        status_code = 200
                        post_value = value[0]
                        to_send = '<html><body><h1>Post Data</h1><pre>{post}</pre></body></html>'.format(post = post_value)
                        filehandler = open(document_root+request_URL,'r')
                        data = filehandler.read()
                        filehandler.close()
                        filehandler = open(document_root+request_URL,'w')
                        filehandler.write(to_send)
                        filehandler.write(data)                                                 #Appends the post data to the requested URL
                        filehandler.close()
                           
            if 'Connection: keep-alive\r' in data_decoded:                                      #Checks if the header has keep-alive string or Not
                keep_alive = 1
              
            if status_code == 400:
                to_send = '<html><body>'+ str(status_code)+ ' Bad Request Reason: ' + reason + '</body></html>'
            filename = document_root + request_URL  
               
            if os.path.isfile(filename):                                                        #Checks the availability of the file
                status_code = 200
                file_present = 1
                filehandle = open(filename, 'rb')
                print('File sent to Client at Port' + str(client_address[1]) + '\t FileName =' + request_URL + '\tAt thread' + str(threading.current_thread()))
                to_send = filehandle.read()
                filesize =os.path.getsize(filename)
                print('Filesize:' + str(filesize))

            elif not os.path.isfile(filename) and status_code == 0  :
                status_code = 404
                reason = 'URL does not exist'
                to_send = '<html><body>'+ str(status_code)+ ' Not Found Reason ' + reason + '</body></html>'
                print('File not Present' + request_URL)
                
            else:
                print('status code:' + str(status_code))
             
            header = header_format(keep_alive, current_date, filesize , status_code, content_type,request_version)      #calls the function to get the header
            send_data(header, status_code, to_send, file_present, client)                                               #Calls the function to send the response
        
            if keep_alive == 1 :
                client.settimeout(keepalive)
                continue
            else:
                client.settimeout(None)
                persistent = 0
                print("CLOSING SOCKET" + str(client_address))
                client.close()
                break
        except socket.timeout:
            print("TIMEOUT HAPPENED")
            persistent = 0
            client.close()
            print('Time when thread Stops: ' + str(time.strftime("%H:%M:%S",time.localtime())))
            total_time = time.clock() - t
            print('Time Taken by the Thread in seconds ==' + str(total_time))
            print("Closing Client at :" + str(client_address))
            print('Exiting Thread: '+ str(threading.current_thread()))
            break
        except IndexError:
            print(" Index ERROR")
            break
        except ConnectionResetError:
            print("Connection Forcibly Closed by Client : " + str(client_address))
            print('Time when thread Stops: ' + str(time.strftime("%H:%M:%S",time.localtime())))
            total_time = time.clock() - t
            print('Time Taken by the Thread in seconds ==' + str(total_time))
            print("Closing Client at :" + str(client_address))
            client.close()
            print('Exiting Thread:' + str(threading.current_thread()))
            break
        except KeyboardInterrupt:
            s_socket.close()
        print("Server Socket Closed")
        
    print("OUT of Thread WHILE of Thread: ==" + str(threading.current_thread()) )
#     print('THREAD WHILE END'*50)
          
        


if __name__ == "__main__":
    try :
        s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        config = configparser.ConfigParser()
        if os.path.isfile('ws.conf'):   
            config.read("ws.conf")
        else:
            print("Congiguration Details not found")
            print("Closing socket")
            s_socket.close()
            sys.exit()
        list_send_extensions = []
        list_valid_extensions = []
        dict_content = {}
        content_type = ConfigSectionMap("content-Type")
        for i in content_type.values():
            first = i.split(',')[0]
            second = i.split(',')[1]
            dict_content[first] = second
        for i in content_type.values():
            string_ = i.split(',')
            list_send_extensions.append(string_[1])
            list_valid_extensions.append(string_[0])
        port_str = ConfigSectionMap("listening port number")['listenport']
        port = int(port_str)
        document_root = ConfigSectionMap("document root")['documentroot']
        directory_index = ConfigSectionMap("Default web page")['directoryindex']
        list_directory_index = directory_index.split(',')
        keepalive_str = ConfigSectionMap("connection timeout")['keepalivetime']
        keepalive = int(keepalive_str)
        host = ''
        BUFFER = 1024
        s_socket.bind((host,port))
        s_socket.listen()
        print('Server Started')
        while 1:
            print("Waiting for new connection")
            client , client_address = s_socket.accept()

            print("A new Accept")
            print(client_address)
            t=threading.Thread(target=server_thread, args= (client, client_address,))
            t.start()
            print(threading.enumerate())

    except KeyboardInterrupt:
        s_socket.close()
        print("Server Socket Closed")
        sys.exit()    
        