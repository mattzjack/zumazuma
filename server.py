import socket
from _thread import *
from queue import Queue

HOST = '128.237.187.239'
PORT = 50014
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("looking for connection")

def serverThread(clientele, serverChannel):
    while True:
        if len(clientele) < 2: continue
        msg = serverChannel.get(True, None)
        print("msg recv: ", msg)
        senderID, msg = int(msg.split("_")[0]), "_".join(msg.split("_")[1:])
        if (msg):
            for cID in clientele:
                if cID != senderID:
                    sendMsg = msg + "\n"
                    print('sending msg to %d:' % cID, repr(sendMsg))
                    clientele[cID].send(sendMsg.encode())
    serverChannel.task_done()

clientele = {}
currID = 0

serverChannel = Queue(100)
start_new_thread(serverThread, (clientele, serverChannel))

def handleClient(client, serverChannel, cID):
    client.setblocking(1)
    msg = ""
    while True:
        msg += client.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverChannel.put(str(cID) + "_" + readyMsg)
            command = msg.split("\n")

while True:
    client, address = server.accept()
    print('currID:', currID)
    msg = ("id %d\n" % (currID))
    print('sending msg to %d:' % currID, repr(msg))
    client.send(msg.encode())
    for cID in clientele:
        msg = ("new_player %d\n" % currID)
        print('sending msg to %d:' % cID, repr(msg))
        clientele[cID].send(msg.encode())
        msg = ('new_player %d\n' % cID)
        print('sending msg to %d:' % currID, repr(msg))
        client.send(msg.encode())
    clientele[currID] = client
    print("connection recieved")
    start_new_thread(handleClient, (client,serverChannel, currID))
    currID += 1
