# webServer
 Pipelined, persistent, optimized, and multi-threaded high performance web server, handling multiple requests 

Author: Rishabh Hastu

What's Implemented?
a. HTTP/1.1
b. HTTP/1.0
b. Persistent Connection
c. Threading
d. Pipelining
e. Performance Evaluation
f. POST

Python Version : 3.5

Whats in the progrm:
1. Accepts the GET request and replies the client based on if the file is present, validity of URL, file not present.
2. If the URL entered is valid and the file requested is correct(GET request), the server searches in its directory for the file and sends it to the server with a 200 Status code header.
3. If the URL entered is not valid(GET request), the server responds with 400 BAD REQUEST header and closes the socket.
4. If the URL entered is valid but the file is not present, the server responds with 404 File not Found and closes the socket.
5. IF the File has a format that the server does not support, then 501 Not Implemented is returned
6. The server is programmed such that GET requests are handled by Threads, in such a way that the same thread serves the socket with same credentials(client IP and Client Port) for a given Keep-Alive Timeer(if the header has Connection: keep-alive header). If the socket requests for another file within the timer, the server replies on the same socket. If there is no keep-alive header in the client request, then the thread closes and does not serve any other request from the client.
7. If any other client requests before the timer expires, the request is served by another thread and the point no. 6 applies to this thread too.
8. Point number 6 and 7 show that the server is multi-threaded as well as Pipelined.
9. The server takes all its parameters from the ws.conf file.
10. For POST, I created a Form Page in HTML, and the webbrowser requested for this form page. When the value in the text box is typed and the submitted, the POST request will be sent to the webserver which further prints the value got from the request in the new webpage, along with the requested URL.

CLIENT PROGRAM:
I have also implemented the client to check the performance of the server. Client is multi threaded for the first 100 requests and the other 100 requests are sequential. For first 100 requests, the client sends GET requests for different files through different sockets while for the subsequent 100 requests in a multi-threaded manner, the client sends GET requests for the same file through the same socket in the same thread.

The server responses by checking whether the header has keep-alive, and then it spawns multiple threads for the first 100 requests and a single thread for the subsequent 100 requests. The first 100 requests are served by different threads and the threads are stopped depending on whether the request has keep-alive header or not. If the header has keep-alive, then the socket remains open for future requests for the given KEEP-ALIVE time. The subsequent 100 requests are served by the same server thread
