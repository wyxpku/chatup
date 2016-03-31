import socket
host = '127.0.0.1'
port = 23333

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

while True:
    data = input('Please input something:')
    if data == 'end':
        break
    s.sendall(data.encode('utf8'))
    ret = s.recv(1024)
    print(ret.decode('utf8'))
s.close()