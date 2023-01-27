#  coding: utf-8 
import socketserver, os



# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright Â© 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
# https://careerkarma.com/blog/python-check-if-file-exists/#:~:text=Python%20Check%20if%20Directory%20Exists&text=path.-,isdir()%20method%20checks%20if%20a%20directory%20exists.,exists%2C%20isdir()%20returns%20True.&text=The%20isdir()%20method%20takes,existence%20you%20want%20to%20verify.
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    # Must do all the work to service a request 
    def handle(self):
        self.data = self.request.recv(1024).strip() # Will receive at most 1024 bytes
        print ("\nGot a request of: %s\n" % self.data)
        
        # Decodes data and splits it to retrieve desired information
        decoded = self.data.decode('utf-8').split("\r\n")
        fullyDecoded = decoded[0]

        #print("This is the decoded data", fullyDecoded)
        
        # Method is retrieved here
        header = decoded[0].split()
        
        response = header[2]
        print("\nThe method is: ", header[0])
        
        path = fullyDecoded.split()[1]
        print("\nThe path request is : ", path)
        htmlResp = "<!DOCTYPE html>\n<head><meta charset='UTF-8'></head>\n<html>\n<body>\n"
        
        # If the HTTP method is not GET, then we return a 405 error
        if header[0] != 'GET':
            htmlResp += "405:Method Not Allowed\n</body>\n</html>"
            response = header[2] + " 405 Method Not Allowed\r\nConnection: Closed\r\n\r\n" + htmlResp
            self.request.sendall(bytearray(response, 'utf-8'))
            return
        
        if path[-1] == "/":
            path += "index.html"
        
        directory = "www" + path
        
        print("\nThe path is: ", path)
        print("\nThe directory is: ", directory)
        
        # If the path does not exist then send a 404 error
        if not os.path.exists(directory):
            htmlResp += "404:Page Not Found\n</body>\n</html>" 
            response = header[2] + " 404 Not Found\r\nContent-Length: " + str(len(htmlResp)) + \
            "\r\nContent-Type: text/html\r\nConnection: Closed\r\n\r\n" + htmlResp
            self.request.sendall(response.encode())
            return
        
        # If the path is found, lets open the content of our html or css file
        if os.path.isfile(directory):
            f = open(directory, 'r')
            content = f.read()
            
            # Set the content type to html or css dependent on the file type
            if directory.endswith("html"):
                contentType = "text/html"
            elif directory.endswith("css"):
                contentType = "text/css"
            else:
                htmlResp += "404:Page Not Found\n</body>\n</html>" 
                response = header[2] + " 404 Not Found\r\nContent-Length: " + str(len(htmlResp)) + \
                "\r\nContent-Type: text/html\r\nConnection: Closed\r\n\r\n" + htmlResp
                self.request.sendall(response.encode())
                return
                
            # Modifying the header to send a success response, including the
            # content type, length & content
            
            response = header[2] + " 200 OK\r\nContent-Type: " + contentType + \
            "\r\nContent-Length: " + str(len(content)) + "\r\n\Connection Closed\r\n\r\n" + content
            self.request.sendall(bytearray(response, 'utf-8'))
                
            f.close()
                
            if os.path.isdir(directory):
                if directory[-1] != "/":
                    code = 301
                    response = header[2] + " 301 Moved Permanently\r\nContent-Type: text/html\r\nLocation: " + "http://127.0.0.1:8080{directory}/\r\n\r\n"
                    self.request.sendall(bytearray(response, 'utf-8'))
        
            # Sending the request for the header, allowing user to receive the html file while
            # connected to the server, encoding with utf-8
        
        self.request.sendall(bytearray(response + " 301 Moved Permanently",'utf-8'))
    
    
  
if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080
    
    socketserver.TCPServer.allow_reuse_address = True
    
    # Create the server, binding to 127.0.0.1 on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()