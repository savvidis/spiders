# import socket
# import sys
# import select

# TOR_CTRL_HOST = "127.0.0.1"
# TOR_CTRL_PORT = 9051
# TOR_CTRL_PWD = ""


# try:
#     tor_c = socket.create_connection((TOR_CTRL_HOST, TOR_CTRL_PORT))
#     r, _, _ = select.select([tor_c], [], [])

#     tor_c.send('AUTHENTICATE "{}"'.format(TOR_CTRL_PWD))
#     tor_c.send('SIGNAL NEWNYM')
#     response = tor_c.recv(10)
#     # print(response)
#     if r:
#         # ready to receive
#         response = tor_c.recv(1024)

#     if response != '250 OK\r\n250 OK\r\n':
#         sys.stderr.write(
#             'Unexpected response from Tor control port: {}\n'.format(response))
#     socket.close()
# except Exception, e:
#     sys.stderr.write(
#         'Error connecting to Tor control port: {}\n'.format(repr(e)))

# import urllib2
# from TorCtl import TorCtl

# proxy_support = urllib2.ProxyHandler({"http": "127.0.0.1:8123"})
# opener = urllib2.build_opener(proxy_support)


# def newId():
#     conn = TorCtl.connect(controlAddr="127.0.0.1",
#                           controlPort=9050, passphrase="")
#     conn.send_signal("NEWNYM")

# for i in range(0, 10):
#     print("case " + str(i + 1))
#     # newId()
#     print("tes")
#     proxy_support = urllib2.ProxyHandler({"http": "127.0.0.1:8123"})
#     urllib2.install_opener(opener)
#     print(urllib2.urlopen("http://www.ifconfig.me/ip").read())


from stem import Signal
from stem.control import Controller


def changetor():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
	print("%%%%%%%% Changed IP %%%%%%%%%%%%%%")

