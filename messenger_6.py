#Importing the necessary libraries
import os
import threading
import logging
import fcntl
import selectors
import sys
from socket import socket, gethostname, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_WR
from typing import Optional, List, TextIO

#Configuring the logging
logging.basicConfig(filename="m.log", filemode='a',format='%(asctime)s.%(msecs)d %(levelname)s/%(name)s::%(message)s',datefmt='%H:%M:%S',level=logging.ERROR)

#Define a class for storing the arguments passed to the program
class Arguments:
    listening: bool
    port: int
    host: str
    def __init__(self, listening: bool, port: int, host: str):
        self.listening = listening
        self.port = port
        self.host = host

#Define a class for synchronizing the threads
class syncLoop:
    __lock: threading.Lock

    __isRunning: bool = True
    
    def __init__(self):
        self.__lock = threading.Lock()
    @property

    # Define a method to get the running status of the loop
    def runningStatus(self):
        status: bool
        with self.__lock:
            status = self.__isRunning
        return status

    # Define a method to terminate the loop
    def terminate(self) -> None:
        logging.info(f"{args.listening} syncLoop.stop() called")
        with self.__lock:
            self.__isRunning = False


#Define a function to send data through a socket
def send(scket: socket, data: str) -> None:
    scket.sendall(data.encode('utf-8'))


#Define a function to receive data through a socket
def receive(scket: socket) -> Optional[str]:
    data = scket.recv(128)
    if data is None:
        logging.debug(f'{args.listening} ==> (userInput) {data} [Data is none]')
        return None

    return data.decode('utf-8')


#Define a function to unregister a socket from a selector object
def betterUnregister(fileobj) -> None:
    try:
        selector.unregister(fileobj)
    except (KeyError, ValueError):
        pass


#Define a function to safely take input from the user
def safeInput(scket: socket) -> None:

    temp = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, temp | os.O_NONBLOCK)
    def userInput(stream: TextIO, mask) -> None:
        if not stream.closed and stream.readable():
            data = stream.read()
            if len(data) == 0:
                shutdown(scket)
                return

            logging.debug(f'{args.listening} ==> (userInput) {data} {[d for d in data]}')
            send(scket, data)
        else:
            shutdown(scket)
    selector.register(sys.stdin, selectors.EVENT_READ, userInput)


#Define a function to safely output data to the user
def safeOutput(scket: socket) -> None:
    def read(scket: socket, mask) -> None:
        data = receive(scket)
        logging.debug(f'{args.listening} <== (read) {data} {[d for d in data]}')
        if not data or len(data) == 0:
            shutdown(scket)
            return
        print(data, end='')
    selector.register(scket, selectors.EVENT_READ, read)


#Define a function to shutdown the program and clean up resources
def shutdown(scket: socket):

    loop.terminate()
    betterUnregister(scket)
    betterUnregister(sys.stdin)
    try:
        data = receive(scket)
        while data is not None and data != '':
            print(data, end='')
            data = receive(scket)
    except:
        pass
    sys.stdin.close()

#Define a function to start the loop
def startLoop() -> None:
    while loop.runningStatus:
        for i, mask in selector.select():
            callback = i.data
            callback(i.fileobj, mask)


#Define the function to start the server
def serverStart(ip: str, port: int) -> socket:
    scket = socket(AF_INET, SOCK_STREAM)
    scket.bind((ip, port))
    return scket


#Server Class
class Server:
    scket: socket
    conn: socket
    running: bool = True

    #method initializes the server socket and sets it to non-blocking mode
    def __init__(self, port: int) -> None:
        self.scket = serverStart(gethostname(), port)
        self.scket.setblocking(False)
        self.scket.listen()

    #method is called when a new connection is accepted
    def accept(self, sock: socket, mask) -> None:
        self.conn, _ = sock.accept()
        self.conn.setblocking(True)
        safeInput(self.conn)
        safeOutput(self.conn)

    #method registers the server socket with the selector and starts the event loop
    def start(self) -> None:
        selector.register(self.scket, selectors.EVENT_READ, self.accept)
        startLoop()
        self.scket.shutdown(SHUT_WR)


def makeConnection(ip: str, port: int) -> socket:
    scket = socket(AF_INET, SOCK_STREAM)
    scket.connect((ip, port))
    return scket


class Client:
    scket: socket
    running: bool = True
    
    #method initializes the client socket and sets it to non-blocking mode, then registers it with the selector for input and output using the safeInput and safeOutput functions.
    def __init__(self, hostname: str, port: int) -> None:
        self.scket = makeConnection(hostname, port)
        self.scket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.scket.setblocking(False)

    #method starts the event loop by calling startLoop()
    def start(self) -> None:
        safeInput(self.scket)
        safeOutput(self.scket)
        startLoop()
        self.scket.shutdown(SHUT_WR)

#function parses command-line arguments to determine whether the script is being run in server or client mode
def checkArgs(argv: List[str]) -> Arguments:
    argv = argv[1:]
    listening = argv[0] == '-l'
    if listening:
        argv = argv[1:]
    port = argv[0]
    host = gethostname()
    if len(argv) == 2:
        host = argv[1]
    return Arguments(listening, int(port), host)


#block, the script creates a default selector and a synchronous event loop. It then parses the command-line arguments, creates either a Server or Client
if __name__ == '__main__':
    selector = selectors.DefaultSelector()
    loop = syncLoop()
    args = checkArgs(sys.argv)
    if args.listening:
        Server(args.port).start()
    else:
        Client(args.host, args.port).start()
