import sipfullproxy
import socketserver
import socket
import my_log


if __name__ == "__main__":
    file = open("proxy.log", "w")
    file.close()

    hostname = socket.gethostname()
    ipaddress = socket.gethostbyname(hostname)

    my_log.inicialization(ipaddress)

    print("Proxy server started at <%s:%s>" % (ipaddress, sipfullproxy.PORT))

    sipfullproxy.recordroute = "Record-Route: <sip:%s:%d;lr>" % (ipaddress, sipfullproxy.PORT)
    sipfullproxy.topvia = "Via: SIP/2.0/UDP %s:%d" % (ipaddress, sipfullproxy.PORT)

    server = socketserver.UDPServer((ipaddress, sipfullproxy.PORT), sipfullproxy.UDPHandler)
    server.serve_forever()
