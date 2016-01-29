#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port=80):
        # use sockets!
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:   
            clientSocket.connect((host, port))
        except socket.error, msg :
            print "Connection error %s" % msg
            sys.exit(1)

        return clientSocket

    def get_code(self, data):
        data = data.split(' ')
        code = data[1]
        return int(code)

    def get_headers(self,data):
        data.split('\r\n')
        return data[1:-2]

    def get_body(self, data):
        body = data.split('\r\n\r\n')
        return body[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def urlparse(self, url):
        #hostname, path, port
        if '://' not in url:
            url = 'http://' + url

        if url.count(':') > 1:
            url = url.split(':')
            ':'.join(url[:2]), ':'.join(url[2:])
            hostname = url[1].replace('/', '')
            url = url[2].split('/',1)
            port = url[0]
            path = '/' + url[1]
        else:
            url = url.split('/')
            '/'.join(url[:3]), '/'.join(url[3:])
            hostname = url[2]
            path = '/' + '/'.join(url[3:])
            if not path:
                path = '/'
            port = None

        #encode queries
        path = path.split('?')
        for each in range(1,len(path)):
            path[each] = urllib.quote(path[each])
        if len(path) > 1:
            path[0] = path[0] + '?'
        path = ''.join(path)

        return port, hostname, path

    def GET(self, url, args=None):
        # parse url
        port, hostname, path = self.urlparse(url)
        print "Port: " + str(port) + " hostname: " + hostname + " path: " + path
        # connect to the host
        if port:
            clientSocket = self.connect(hostname, int(port))
        else:
            clientSocket = self.connect(hostname)
        # GET request to send
        request = "GET {} HTTP/1.1\r\nUser-Agent: Cody's Client\r\nHost: {}\r\nConnection: close\r\nAccept:*/*\r\n\r\n".format(path, hostname)
        # send the request over the socket
        clientSocket.sendall(request)
        # recieve the response
        response = self.recvall(clientSocket)
        # print response for user 
        print response + '\n'
        # get response for admin
        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #parse
        port, hostname, path = self.urlparse(url)
        print "Port: " + str(port) + " hostname: " + hostname + " path: " + path
        # connect to the host
        if port:
            clientSocket = self.connect(hostname, int(port))
        else:
            clientSocket = self.connect(hostname)

        #encode arguements
        if args != None:
            query = urllib.urlencode(args)
            length = len(query)
        else:
            query=""
            length = 0

        request = "POST {} HTTP/1.1\r\nUser-Agent: Cody's Client\r\nHost: {}\r\nAccept:*/*\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{}".format(path, hostname, length, query)
        clientSocket.sendall(request)

        response = self.recvall(clientSocket)

        print response + '\n'

        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        #user command
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        #GET
        print client.command( sys.argv[1] ) 
