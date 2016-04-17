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


def connect_allowed(ip, port=None):
    if port is None:
        for user in users:
            if user.ip == tmp_ip:
                return False
        return True
    else:
        for user in users:
            if user.ip == tmp_ip and (user.tcp_port == port or user.udp_port == port):
                return False
        return True


def ip2int(ip):
    return int(ipaddress.IPv4Address(ip))


def int2ip(ip):
    return str(ipaddress.IPv4Address(ip))


def get_user_list():
    user_num = len(users)
    ret = user_num.to_bytes(4, byteorder='big')
    for tuser in users:
        ret = ret + tuser.ip.to_bytes(4, byteorder='big')
        ret = ret + tuser.tcp_port.to_bytes(2, byteorder='big')
        ret = ret + tuser.user_name
    return ret


def client_update_user_list(cuser=None):
    response = get_user_list()
    for user in users:
        if cuser is not None and user == cuser:
            print('DEBUG: client_update_user_list')
            print(b'\x05' + response)
            server.sendto(b'\x02' + response, (int2ip(user.ip), user.udp_port))
        else:
            print('DEBUG: client_update_user_list')
            print(b'\x05' + response)
            server.sendto(b'\x05' + response, (int2ip(user.ip), user.udp_port))


while True:
    data, address = server.recvfrom(DEFAULT_BUF_SIZE)
    print(data)
    if not data:
        print('DEBUG: received data empty')
        continue

    req = data[0]
    # print(req)
    print(type(req), req)
    if req == 1:
        # client login
        print('DEBUG: case login')
        tmp_tcp_port = int.from_bytes(data[1:3], byteorder='big')
        tmp_name = data[3:23]
        tmp_ip = ip2int(address[0])
        tmp_udp_port = address[1]
        if connect_allowed(tmp_ip, tmp_tcp_port):
            print('INFO: %s port %s connected!' % (address[0], tmp_tcp_port))
            tmp_user = User(tmp_ip, tmp_tcp_port, tmp_udp_port, tmp_name)
            users.append(tmp_user)
            client_update_user_list(cuser=tmp_user)
        else:
            print('ERROR: Connection refused!')
            server.sendto(b'\x06', address)
    elif req == 3:
        # client logout
        print('DEBUG: case logout')
        tmp_ip = ip2int(address[0])
        tmp_port = address[1]
        if connect_allowed(tmp_ip, tmp_port):
            print('ERROR: Haven\'t logged in!')
            server.sendto(b'\x06', address)
        else:
            users = list(filter(lambda x: not (x.ip == tmp_ip and x.udp_port == tmp_port), users))
            server.sendto(b'\x04', address)
            client_update_user_list()

server.close()