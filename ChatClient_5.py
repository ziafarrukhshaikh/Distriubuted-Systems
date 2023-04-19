import sys
import socket
from threading import Thread


def send(socket):
    while True:
        data = sys.stdin.readline()
        if len(data) == 0:
            break
        socket.send(data.encode("ascii", "replace"))


def recieve(socket):
    while True:
        data = socket.recv(1024).decode("ascii", "replace")
        if len(data)==0:
            break
        print(data)

def startThreadsHelper(scket):
    _senderThread = Thread(target=send, args=(scket,))
    _receiverThread = Thread(target=recieve, args=(scket,))
    _senderThread.daemon = True
    _receiverThread.daemon = True
    _senderThread.start()
    _receiverThread.start()
    return _senderThread, _receiverThread

def startThreads(socket):
    senderThread, reciverThread = startThreadsHelper(scket)
    return senderThread, reciverThread

if __name__ == "__main__":
    args = len(sys.argv) 
    if args != 2:
        usage(sys.argv[0])
        sys.exit()
    scket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    scket.connect(('Localhost', int(sys.argv[1])))
    clientSend, clientReceive = startThreads(scket)

    while clientSend.is_alive() and clientReceive.is_alive():
        continue
    scket.close()