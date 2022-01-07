import upnpy
import lxml.etree as etree

upnp = upnpy.UPnP()
upnp.ssdp.socket.bind(("192.168.0.213", 1901))
devices = upnp.discover()
print(devices)

device = next(device for device in devices if device.friendly_name == "Gerbera")

services = device.get_services()
print(services)

service = device["ContentDirectory"]
print(service.get_actions())

result = service.Browse(ObjectID=0, BrowseFlag="BrowseDirectChildren", Filter="", StartingIndex=0, RequestedCount=100,
                        SortCriteria="")
xml = result["Result"]
print(xml)
result = service.Browse(ObjectID=5, BrowseFlag="BrowseDirectChildren", Filter="", StartingIndex=0, RequestedCount=100,
                        SortCriteria="")

xml = result["Result"]
print(xml)

root = etree.fromstring(xml.encode())
for element in root.xpath("//didl:item[./upnp:class[text() = 'object.item.videoItem']]/dc:title",
                          namespaces={"dc": "http://purl.org/dc/elements/1.1/",
                                      "didl": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/",
                                      "upnp": "urn:schemas-upnp-org:metadata-1-0/upnp/"}):
    print(element.text)
