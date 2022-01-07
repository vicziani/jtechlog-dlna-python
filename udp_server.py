from socket import *
from kiss_headers import parse_it
import platform

INTERFACE_IP = "192.168.0.213"

print("Running server")

udp_server = socket(AF_INET, SOCK_DGRAM)
udp_server.bind(("", 1900))
mreq = inet_aton("239.255.255.250") + inet_aton(INTERFACE_IP)
udp_server.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

while True:
    data, address = udp_server.recvfrom(1500)
    text = data.decode("utf-8")
    method = text.split()[0]
    headers = parse_it(text)
    print(text)
    if method == "M-SEARCH" and headers.ST == "upnp:rootdevice":
        print("Handle M-SEARCH for upnp:rootdevice")
        response = f"""HTTP/1.1 200 OK
EXT:
LOCATION: http://{INTERFACE_IP}:8080/rootDesc.xml
SERVER: {platform.system()}/{platform.release()}, UPnP/1.0, JTechLog UPnP Server 0.0.1
ST: upnp:rootdevice
USN: uuid:fea4bf14-6da5-11ec-90d6-0242ac120003::upnp:rootdevice

""".replace("\n", "\r\n")

        udp_server.sendto(response.encode("utf-8"), address)
