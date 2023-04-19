from threading import Thread
import sys
import socket
import threading

def sendToClients(scket):
    name = scket.recv(1024).decode().strip()
    while True:
        data = scket.recv(1024)
        if len(data)!=0:
            print('\nrecieved: ' + data.decode("ascii", "replace"), end='')

        else:
            scket.close()
            clientList.remove(scket)
            break
        data = name.encode("ascii","replace") + str(": ").encode() + data

        for clients in clientList:
            if clients is not scket:
                clients.send(data)


def addClient(scket):
    while True:
        scket, addr = serversocket.accept()
        clientList.append(scket)
        senderThread = threading.Thread(target=sendToClients, args=(scket,)).start()

if __name__ == "__main__":
    clientList = []
    args = len(sys.argv)

    if args != 2:
        usage(sys.argv[0])
        sys.exit()

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('localhost', int(sys.argv[1])))
    serversocket.listen(10)

    addingThread = threading.Thread(target=addClient, args=(serversocket,))
    addingThread.start()
