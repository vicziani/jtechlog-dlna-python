import asyncio
from kiss_headers import parse_it
from socket import *
import platform
# import signal
from aiohttp import web

MULTICAST_PORT = 1900
MULTICAST_GROUP = "239.255.255.250"


class SsdpProtocol(asyncio.BaseProtocol):
    def __init__(self, interface_ip):
        self.transport = None
        self.interface_ip = interface_ip

    def connection_made(self, transport):
        print("UDP connection made")
        self.transport = transport

    def connection_lost(self, ex):
        print("UDP connection lost")

    def datagram_received(self, data, address):
        text = data.decode("utf-8")

        method = text.split()[0]
        headers = parse_it(text)
        if method == "M-SEARCH" and headers.ST == "upnp:rootdevice":
            print("Handle M-SEARCH")
            response = f"""HTTP/1.1 200 OK
EXT:
LOCATION: http://{self.interface_ip}:8080/rootDesc.xml
SERVER: {platform.system()}/{platform.release()}, UPnP/1.0, JTechLog UPnP Server 0.0.1
ST: upnp:rootdevice
USN: uuid:fea4bf14-6da5-11ec-90d6-0242ac120003::upnp:rootdevice

""".replace("\n", "\r\n")

            self.transport.sendto(response.encode("utf-8"), address)


async def run_udp_server(interface_ip):
    print("Starting UDP server")

    udp_server = socket(AF_INET, SOCK_DGRAM)
    udp_server.bind(("", MULTICAST_PORT))
    mreq = inet_aton(MULTICAST_GROUP) + inet_aton(interface_ip)
    udp_server.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: SsdpProtocol(interface_ip),
        sock=udp_server)

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    except asyncio.CancelledError:
        print("Cancelled UDP server")
    finally:
        transport.close()


class HttpHandler:

    def __init__(self, interface_ip, http_port):
        self.interface_ip = interface_ip
        self.http_port = http_port

    async def handle(self, request):
        print("Handle HTTP request to 'rootDesc.xml'")
        text = f"""<?xml version="1.0"?>
<root xmlns="urn:schemas-upnp-org:device-1-0" xmlns:dlna="urn:schemas-dlna-org:device-1-0">
<specVersion>
<major>1</major>
<minor>0</minor>
</specVersion>
<device>
    <deviceType>upnp:rootdevice</deviceType>
    <friendlyName>JTechLog</friendlyName>
</device>
<URLBase>http://{self.interface_ip}:{self.http_port}/</URLBase>
</root>
"""
        return web.Response(text=text)


async def run_http_server(interface_ip):
    print("Starting HTTP server")
    app = web.Application()
    handler = HttpHandler(interface_ip, 8080)
    app.add_routes([web.get('/rootDesc.xml', handler.handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=interface_ip, port=8080)
    await site.start()

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    except asyncio.CancelledError:
        print("Cancelled HTTP server")


class SignalHandler:

    def __init__(self, tasks):
        self.tasks = tasks

    def handle(self):
        print("Got SIGINT signal")
        for task in self.tasks:
            task.cancel()


async def run_servers(interface_ip):

    udp_server_task = asyncio.ensure_future(run_udp_server(interface_ip))
    http_server_task = asyncio.ensure_future(run_http_server(interface_ip))

    # loop = asyncio.get_event_loop()
    # signal_handler = SignalHandler([udp_server_task, http_server_task])
    # loop.add_signal_handler(signal.SIGINT, signal_handler.handle)

    await asyncio.gather(udp_server_task, http_server_task)

print("Starting servers")
asyncio.run(run_servers("192.168.0.213"))
