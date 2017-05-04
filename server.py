import socket, time
from _thread import *
from queue import Queue

HOST = ''
PORT = 50014
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(BACKLOG)

num_ready_players = dict()

def serverThread(clientele, serverChannel):
    sent = False
    while True:
        if not sent and len(num_ready_players) == 2:
            sent = True
            msg = 'start\n'
            for cID in clientele:
                clientele[cID].send(msg.encode())
        msg = serverChannel.get(True, None)
        msg_sent = False
        original_msg = msg
        senderID, msg = int(msg.split("_")[0]), "_".join(msg.split("_")[1:])
        for cID in clientele:
            if cID != senderID:
                sendMsg = msg + "\n"
                clientele[cID].send(sendMsg.encode())
                msg_sent = True
        if not msg_sent:
            serverChannel.put(original_msg)
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
            can_put = True
            if readyMsg.startswith('ready'):
                can_put = False
                num_ready_players[cID] = True
            if can_put:
                serverChannel.put(str(cID) + "_" + readyMsg)
            msg = "\n".join(command[1:])
            command = msg.split("\n")

while True:
    client, address = server.accept()
    msg = ("id %d\n" % (currID))
    client.send(msg.encode())
    for cID in clientele:
        msg = ("new_player %d\n" % currID)
        clientele[cID].send(msg.encode())
        msg = ('new_player %d\n' % cID)
        client.send(msg.encode())
    clientele[currID] = client
    start_new_thread(handleClient, (client,serverChannel, currID))
    currID += 1
