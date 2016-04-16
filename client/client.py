import socket

DEFAULT_BUF_SIZE = 2048

host = '127.0.0.1'
port = 23333

saddr = (host, port)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    msg = input()
    if not msg:
    	break
    client.sendto(msg.encode('utf8'), saddr)
    data, addr = client.recvfrom(DEFAULT_BUF_SIZE)
    print('received:', data.decode('utf8'), 'from', addr)

client.close()