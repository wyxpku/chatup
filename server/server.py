import socket
import ipaddress

DEFAULT_BUF_SIZE = 2048
SERVER_IP = '127.0.0.1'
SERVER_PORT = 23333

server_address = (SERVER_IP, SERVER_PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(server_address)


class User:
    def __init__(self, ip, tcp_port, udp_port, user_name):
        # ip: int
        self.ip = ip
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        # user_name: 20 bytes, end with several 0x00, not decoded
        self.user_name = user_name

users = []


def connect_allowed(ip):
    for user in users:
        if user.ip == tmp_ip:
            return False
    return True


def ip2int(ip):
    return int(ipaddress.IPv4Address(ip))


def int2ip(ip):
    return str(ipaddress.IPv4Address(ip))


def get_user_list():
    ret = b'2'
    user_num = len(users)
    ret = ret + user_num.to_bytes(4, byteorder='big')
    for user in users:
        ret = ret + user.ip.to_bytes(4, byteorder='big')
        ret = ret + user.tcp_port.to_bytes(2, byteorder='big')
        ret = ret + user.user_name
    return ret

while True:
    data, addr = server.recvfrom(DEFAULT_BUF_SIZE)
    # print('received:', data.decode('utf8'), 'from', caddr)
    if not data:
        print('DEBUG: received data empty')
        continue
    req = data[0]
    if req == 0x1:
        # client login
        tmp_tcp_port = (int(data[1]) << 8) + data[2]
        tmp_name = data[3:23]
        tmp_ip = addr[0]
        tmp_udp_port = addr[1]
        if connect_allowed(tmp_ip):
            print('ERROR: Connection refused!')
            server.sendto('ERROR: Connection refused!'.encode('utf8'), addr)
        else:
            tmp_user = User(tmp_ip, tmp_tcp_port, tmp_udp_port, tmp_name)
            users.append(tmp_user)
            response = get_user_list()
            server.sendto(response, addr)
    elif req == 0x3:
        # client logout
        pass
    else:
        continue
    # server.sendto('success'.encode('utf8'), caddr)

server.close()