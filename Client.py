import socket
import sys



def send(ip, port, message):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    
    try:
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))
        return response.split(None, 1)
    
    finally:
        sock.close()



def get(ip, port, key):
    return send(ip, port, "get {0}".format(key))

def add(ip, port, key, data):
    return send(ip, port, "add {0} {1}".format(key, data))

def add_node(ip, port, key):
    return send(ip, port, "addnode {0}".format(key))

def rm_node(ip, port, key):
    return send(ip, port, "rmnode {0}".format(key))

def stats(ip, port):
    return send(ip, port, "stats")

def performance(ip,port):
	return send(ip,port, "performance")

def test_load_balancing(ip,port,num_node,num_data):
	return send(ip,port, "test {0} {1}".format(num_node,num_data))

def clean(ip,port):
    return send(ip,port,"clean")



if __name__ == "__main__":

    ip, port = sys.argv[1], int(sys.argv[2])
    while True:
        command = input("> ")
        send(ip, port, command)