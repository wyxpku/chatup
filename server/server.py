import socket

host = '127.0.0.1'
port = 23333
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

while True:
    conn, addr = s.accept()
    print('Connected by', addr)
    while True:
    	data = conn.recv(1024)
    	tmpstr = data.decode('utf8')
    	print('Received:', tmpstr)
    	if tmpstr == 'disc':
    		conn.sendall(b'Bye. Good luck')
    		conn.close()
    		break
    	else:
    		conn.sendall(b'Echo: ' + tmpstr.encode('utf8'))