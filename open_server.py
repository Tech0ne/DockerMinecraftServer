from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from random import randint, choice, seed
from time import sleep

ip = input("> Enter server IP: ")

_seed = 0
for i in range(len(ip)):
    _seed += ord(ip[i]) * (i + 1)

seed(_seed)

seq = []

for _ in range(randint(4, 6)):
    seq.append((randint(1024, 65535), choice(['TCP', 'UDP'])))

print("Knock, knock...")

for e in seq:
    use_tcp = e[1] == 'TCP'
    s = socket(AF_INET, (SOCK_STREAM if use_tcp else SOCK_DGRAM))
    s.setblocking(False)
    socket_address = (ip, e[0])
    if use_tcp:
        s.connect_ex(socket_address)
    else:
        s.sendto(b'', socket_address)
    s.close()
    sleep(0.5)

print("Welcome to the wonderworld")
