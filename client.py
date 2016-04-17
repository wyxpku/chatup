import socket
import ipaddress
import re
import threading

DEFAULT_BUF_SIZE = 2048
SERVER_IP = '127.0.0.1'
LOCAL_IP = '127.0.0.1'
SERVER_PORT = 23333
TCP_PORT = 23335
server_address = (SERVER_IP, SERVER_PORT)


class User:
    def __init__(self, ip, port, name):
        # ip: int
        self.ip = ip
        self.port = port
        # user_name: 20 bytes, end with several 0x00, not decoded
        self.name = name


def ip2int(ip):
    return int(ipaddress.IPv4Address(ip))


def int2ip(ip):
    return str(ipaddress.IPv4Address(ip))


def is_ip(tmp_str):
    expression = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    if expression.match(tmp_str):
        return True
    else:
        return False


def aligned_name(raw_name):
    ret = raw_name.encode('utf8')
    while len(ret) < 20:
        ret = ret + b'\x00'
    return ret


def get_new_user_list(tmp_data):
    new_list = []
    num = int.from_bytes(tmp_data[1:5], byteorder='big')
    print('DEBUG: get_new_user_list')
    print(tmp_data)
    for i in range(num):
        begin = 5 + i * 26
        tmp_ip = int2ip(int.from_bytes(tmp_data[begin: begin + 4], byteorder='big'))
        tmp_port = int.from_bytes(tmp_data[begin + 4: begin + 6], byteorder='big')
        raw_name = tmp_data[begin + 6: begin + 26]
        tmp_name = raw_name[:raw_name.find(b'\x00')].decode('utf8')
        tmp_user = User(tmp_ip, tmp_port, tmp_name)
        new_list.append(tmp_user)
    return new_list

mutex = threading.Lock()
users = []
tcp_socket = None
udp_socket = None


def recv_msg():
    global tcp_socket
    while True:
        conn, addr = tcp_socket.accept()
        try:
            conn.settimeout(5)
            buf = conn.recv(DEFAULT_BUF_SIZE)
            if buf is not None:
                print('New Message from', addr, buf[:-1].decode('utf8'))
        except:
            pass


def update():
    global mutex, users, udp_socket
    while True:
        tmp_data, tmp_addr = udp_socket.recvfrom(DEFAULT_BUF_SIZE)
        if tmp_data is None:
            continue
        if tmp_data[0] == 5:
            if mutex.acquire():
                users = get_new_user_list(tmp_data)
                mutex.release()
                print('INFO: user list updated!')
                print_user_list()
    return


def print_user_list():
    print('---------------------------------------')
    print('|%10s|%5s|%20s|' % ('ip', 'port', 'name'))
    for user in users:
        print('---------------------------------------')
        print('|%10s|%5s|%20s|' % (user.ip, user.port, user.name))
    print('---------------------------------------')


def connect():
    global udp_socket, users
    # get user name
    name = input('Please input your name( <= 20 bytes): ')
    while len(name) > 20:
        name = input('Please input your name( <= 20 bytes): ')

    # get login parameters
    tmp_data = b'\x01'
    tmp_data = tmp_data + TCP_PORT.to_bytes(2, byteorder='big')
    tmp_data = tmp_data + aligned_name(name)
    # log in
    udp_socket.sendto(tmp_data, server_address)

    tmp_data, tmp_addr = udp_socket.recvfrom(DEFAULT_BUF_SIZE)
    code = tmp_data[0]
    if code == 2:
        users = get_new_user_list(tmp_data)
        return True
    else:
        return False


if __name__ == '__main__':
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    TCP_PORT = int(input('Please input port:'))
    connected = connect()
    if not connected:
        print('ERROR: connection failed!')
        udp_socket.close()
        exit()
    print_user_list()
    # run a tcp server, and listen for new message in a new thread
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((LOCAL_IP, TCP_PORT))
    # max connection num
    tcp_socket.listen(5)
    tcp_thread = threading.Thread(target=recv_msg)
    tcp_thread.start()

    # create a new thread, listen for upadte information
    update_thread = threading.Thread(target=update)
    update_thread.start()

    while True:
        cmd = input('chatup>')
        if cmd == 'list':
            print_user_list()
        elif cmd == 'exit':
            udp_socket.sendto(b'\x03', server_address)
            data, addr = udp_socket.recvfrom(DEFAULT_BUF_SIZE)
            if data[0] == 4:
                print('INFO: Logged out successfully!')
                udp_socket.close()
                exit(1)
        elif cmd.index('chat') == 0:
            index_t = cmd.find('-t')
            index_m = cmd.find('-m')
            if index_m == -1 or index_t == -1 or index_t >= index_m:
                print('ERROR: Wrong command!')
            tar_ip_and_port = cmd[index_t+3:index_m-1]
            msg = cmd[index_m + 3:]
            tar_ip, tar_port = tar_ip_and_port.split(':')
            if not is_ip(tar_ip):
                print('ERROR: IP is wroing!')
            tar_port = int(tar_port)
            tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                tmp_socket.connect((tar_ip, tar_port))
                tmp_socket.send(msg.encode('utf8') + b'\x00')
                tmp_socket.close()
            except:
                print('ERROR: Filed sending message! Plese try again.')
        elif cmd == 'help':
            print('Commands:')
            print('    list: list all users that connected to the server')
            print('    exit: disconnect with the server and exit')
            print('    tell: send message, example: tell -t 192.168.0.1:23334 -m \'Hello! How are you?\'')
            print('    help: see help information')
        else:
            print('ERROR: No such command!', 'Input help to get more information.')
