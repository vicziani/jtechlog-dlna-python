import socket

msg = '''M-SEARCH * HTTP/1.1
HOST:239.255.255.250:1900
ST:upnp:rootdevice
MX:2
MAN:"ssdp:discover"

'''.replace("/n", "/r/n")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
client_socket.bind(("192.168.0.213", 1901))  # 1.
client_socket.settimeout(2)
client_socket.sendto(msg.encode("utf-8"), ('239.255.255.250', 1900))

try:
    while True:
        data, addr = client_socket.recvfrom(65507)
        print(addr)
        print(data.decode("utf-8"))
except socket.timeout:
    pass
