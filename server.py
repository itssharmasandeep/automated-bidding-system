import socket
import threading
import time

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# Using 15 clients and their pre-set highest values
CLIENT_HIGHEST_VALUES = [13000.0, 15000.0, 15000.0, 18000.0, 19500.0, 20000.0,
                         17000.0, 17000.0, 12500.0, 14500.0, 16000.0, 15500.0, 15500.0, 13000.0, 13500.0]
# Using 5 products and their initial price
PRODUCTS = ["Watch", "Ring", "Shoe", "Baseball", "Hat"]
PRODUCTS_PRICE = [500.0, 900.0, 400.0, 600.0, 350.0]
MAX_BIDS = 50

# Server creation

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# These are all the variables

clients = []
numberOfClients = 0
clientsAdded = 0
totalBids = 0
biddingStarted = False
biddingEnded = False
bidWinners = [-1, -1, -1, -1, -1]
currentBidAmounts = [500.0, 900.0, 400.0, 600.0, 350.0]

# This function is to broadcat msg to every client


def broadcastMessage(msg):
    time.sleep(1)
    for client in clients:
        client.send(msg.encode(FORMAT))

# This function is to update bidding winner data


def updateData(bidClient, prodId, bidAmt):
    bidWinners[prodId] = bidClient
    currentBidAmounts[prodId] = bidAmt

# This function is to print all winners


def showWinners():
    productId = 0
    print(".......BIDDING ENDED.......")
    print("And winners are.....")
    for bidWinner in bidWinners:
        if bidWinner != -1:
            print(
                f"For product: {PRODUCTS[productId]} winner is: {bidWinner} wth amount: {currentBidAmounts[productId]}")
        else:
            print(
                f"For product: {PRODUCTS[productId]} winner is NO ONE because of no bidding for this product")
        productId += 1

# This function is to end bidding for everyone


def endBidding():
    global biddingEnded
    biddingEnded = True
    time.sleep(1)
    showWinners()
    broadcastMessage(f"BIDDING_ENDED")
    for client in clients:
        client.close()


# This function is to print all the products

def print_list_of_products():
    print("List of products to be selected")
    i = 0
    for prod in PRODUCTS:
        print(f"{prod} :: {PRODUCTS_PRICE[i]}")
        i = i+1

# This function is to handle client messages


def handle_client(connection, addr):
    global clients
    global clientsAdded
    global biddingStarted
    global bidWinners
    global currentBidAmounts
    global totalBids
    clientId = clientsAdded
    clientsAdded += 1
    clients.append(connection)
    print(f"[CONNECTIONS] Client {clientId} connected")
    connection.send(f"CONNECTED {clientId}".encode(FORMAT))
    connection.send(f"PRESET {CLIENT_HIGHEST_VALUES[clientId]}".encode(FORMAT))
    connected = True
    if ((numberOfClients - 1) == clientId):
        print(f"All clients connected... Bidding will be started soon..")
        biddingStarted = True
        broadcastMessage(f"START_BID 0 {numberOfClients}")
    while connected:
        if totalBids == MAX_BIDS:
            endBidding()
            break
        if biddingStarted and (biddingEnded == False):
            msg_length = connection.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = connection.recv(msg_length).decode(FORMAT)
                msgList = msg.split()
                msgType = msgList[0]
                if msgType == "BID":
                    prodId = int(msgList[1])
                    bidAmt = float(msgList[2])
                    updateData(clientId, prodId, bidAmt)
                    print(
                        f"[BID] Client {clientId} put a bid of amount: {bidAmt} , for product {PRODUCTS[prodId]}")
                    broadcastMessage(
                        f"BID {clientId} {prodId} {bidAmt}")
                    totalBids += 1
                elif msgType == "NO_BID":
                    msgText = msgList[1]
                    print(
                        f"[NO BID] from the client {clientId} with reason: {msgText}")
                    broadcastMessage(f"NO_BID {clientId} {msgText}")
                    totalBids += 1

# This function is to start a server and listen for clients connection


def start():
    global numberOfClients
    global totalBids
    global biddingEnded
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    print_list_of_products()
    if numberOfClients > 15 or numberOfClients < 1:
        print(f"Please enter how many clients you want to be added(max 15)?")
        numberOfClients = input()
        numberOfClients = int(numberOfClients)
    while (not biddingEnded):
        if (numberOfClients > (threading.active_count() - 1)) and biddingStarted == False:
            print(
                f"Ok! Waiting for {numberOfClients - (threading.active_count() -1)} more clients")
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()


start()
