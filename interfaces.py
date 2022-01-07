import socket

interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
print(interfaces)