from Ring import ConsistentHashedRing
import socket
import socketserver
import threading
import json
import re
import zlib
import random
import time



node = None
key_regex = re.compile("\d\.\d\.\d\.\d:\d")
K=[]#stores keys added



ADD_NODE = {
    "cmd": "addnode",
    "args": 1,
    "response_ok": 1,
    "response_err": -1,
}
RM_NODE = {
    "cmd": "rmnode",
    "args": 1,
    "response_ok": 2,
    "response_err": -2,
}
ADD = {
    "cmd": "add",
    "args": 2,
    "response_ok": 3,
    "response_err": -3,
}
GET = {
    "cmd": "get",
    "args": 1,
    "response_ok": 4,
    "response_err": -4,
}
STATS = {
    "cmd": "stats",
    "args": 0,
    "response_ok": 5,
    "response_err": -5,
}
PERF = {
    "cmd": "per",
    "args": 0,
    "response_ok": 6,
    "response_err": -6,
}
TEST = {
    "cmd": "test",
    "args": 2,
    "response_ok": 7,
    "response_err": -7,
}
CLEAN = {
    "cmd": "clean",
    "args": 2,
    "response_ok": 8,
    "response_err": -8,
}
ERROR = {
    "cmd": None,
    "args": 0,
    "response_ok": 0,
    "response_err": -99,
}



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):



    def handle(self):

        # Get data and split
        data = str(self.request.recv(1024), 'utf-8').split(None, 2)
        command = data[0]
        global ring



        if command == ADD_NODE["cmd"]:
            if len(data)-1 < ADD_NODE["args"]:
                response = "-99 Wrong parameters"
            else:
                if key_regex.search(data[1]):
                    self._add_node(data[1])
                    response = "{0} {1}".format(ADD_NODE["response_ok"], "added node")
                else:
                    response = "{0} {1}".format(ADD_NODE["response_err"], "bad argument")



        elif command == RM_NODE["cmd"]:
            if len(data)-1 < RM_NODE["args"]:
                response = "-99 Wrong parameters"
            else:
                if key_regex.search(data[1]):
                # if True:
                    self._rm_node(data[1])
                    response = "{0} {1}".format(RM_NODE["response_ok"], "removed node")
                else:
                    response = "{0} {1}".format(RM_NODE["response_err"], "bad argument")



        elif command == ADD["cmd"]:
            if len(data)-1 < ADD["args"]:
                response = "-99 Wrong parameters"
            else:
                try:
                    r = self._add_data(data[1], data[2])
                    if r == True:
                        response = "{0} {1}".format(ADD["response_ok"], "Added data")
                    else:
                        response = "{0} {1}".format(ADD["response_err"], "Ring Empty")

                except ConnectionRefusedError:
                    response = "{0} {1}".format(ADD["response_err"], "Connection error")



        elif command == GET["cmd"]:
            if len(data)-1 < GET["args"]:
                response = "-99 Wrong parameters"
            else:
                try:
                    res_data = self._get_data(data[1])
                    if res_data == None:
                        response = "{0} {1}".format(GET["response_err"], "Missed data")
                    else:
                        response = "{0} {1}".format(GET["response_ok"], res_data)
                except ConnectionRefusedError:
                    response = "{0} {1}".format(GET["response_err"], "Connection error")



        elif command == STATS["cmd"]:
            if len(data)-1 < STATS["args"]:
                response = "-99 Wrong parameters"
            else:
                response = json.dumps(ring.stats())



        elif command == PERF["cmd"]:
            if len(data)-1 < PERF["args"]:
                response = "-99 Wrong parameters"
            else:
                response = json.dumps(ring.performance())



        elif command == CLEAN["cmd"]:
            if len(data)-1 < CLEAN["args"]:
                response = "-99 Wrong parameters"
            else:
                global K
                K=[]
                response = json.dumps(ring.clean(data[1],data[2]))



        elif command == TEST["cmd"]:
            if len(data)-1 < TEST["args"]:
                response = "-99 Wrong parameters"
            else:
                try:
                    self._test(data[1], data[2])
                    response = "{0} {1}".format(ADD["response_ok"], "Added data and node")

                except ConnectionRefusedError:
                    response = "{0} {1}".format(ADD["response_err"], "Connection error")



        else:
            response = "-99 Wrong command"

        self.request.sendall(bytes(response, 'utf-8'))



    def _test(self,num_nodes,num_data):
        
        print(" "+"-"*50)
        num_data=int(num_data)
        num_nodes=int(num_nodes)

        start = time.time()

        # add cache servers
        for i in range(num_nodes):
            key = '{}.{}.{}.{}:{}'.format(random.sample(range(0,255),1)[0],random.sample(range(0,255),1)[0],random.sample(range(0,255),1)[0],random.sample(range(0,255),1)[0],random.sample(range(1000,9999),1)[0])
            self._add_node(key)

        end = time.time()

        server_print("Time to add nodes",str(end-start))

        start = time.time()
        
        # add data in cache servers
        for i in range(num_data):
            key = random.randint(0,999999)
            data = random.randint(0,999999)
            self._add_data(key,data)
        end = time.time()

        server_print("Time to add data",str(end-start))

        # check hit ratio
        global K
        hr=0
        for i in range(int(len(K)/2)):
            j=random.randint(0,len(K)-1)
            if self._get_data(K[j]) != None:
                hr+=1
        server_print("Hit Ratio",str(100*(hr/int(len(K)/2)))+"%")

        print(" "+"-"*50)



    def _get_data(self, key):
        
        global ring
        node = ring.get(key)

        if node == None:
            return None

        return node.get_data(key)     
        


    def _add_data(self, key, data):
        
        global ring,K
        node = ring.get(key)

        if node == None:
            return False

        K.append(key)
        node.add_data(key,data)
        return True



    def _add_node(self, key):

        global ring
        ring.add(key)



    def _rm_node(self, key):

        global ring
        a=ring.remove(key)
        
        # redistribution
        if a:
            for k,v in a.items():
                self._add_data(k,v)



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass



class NodeServer(object):

    def __init__(self, host="127.0.0.1", port=8080):

        self._host = host
        self._port = port
        self._server = None



    def _set_environment(self):

        global ring
        ring = ConsistentHashedRing(zlib.crc32)



    def run(self):

        try:
            self._set_environment()
            print ("Node listening {0}:{1}".format(self._host, self._port))
            self._server = ThreadedTCPServer((self._host, self._port), ThreadedTCPRequestHandler)
            server_thread = threading.Thread(target=self._server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            print("Server loop running in thread:", server_thread.name)
            self._server.serve_forever()

        except KeyboardInterrupt:
            print("^C received, shutting down the node")
            
            self._server.shutdown()



def server_print(s1,s2):
    print("|",end="")
    print(s1.ljust(25),end="")
    print(s2.ljust(25),end="|\n")



server = NodeServer()
server.run()