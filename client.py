import socket
import time
import random

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
BID_LIMIT = 80
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

# Using 5 products and their initial price
PRODUCTS = ["Watch", "Ring", "Shoe", "Baseball", "Hat"]
PRODUCTS_PRICE = [500.0, 900.0, 400.0, 600.0, 350.0]
MAX_BIDS = 50

# Connect client to server


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# Initialize variables


clientId = -1
clientPresetValue = -1.0
bidWinners = [-1, -1, -1, -1, -1]
currentBidAmounts = [500.0, 900.0, 400.0, 600.0, 350.0]
lastBidBy = -1
numberOfClients = 0
totalBids = 0

# This function is to send message


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

# This function is to update data


def updateData(bidClient, prodId, bidAmt):
    bidWinners[prodId] = bidClient
    currentBidAmounts[prodId] = bidAmt

# This function is to check whether client is eligible to bid or not


def amIEleigibleClientToBid():
    if (lastBidBy+1) % numberOfClients == clientId:
        return True
    return False

# This function is to check bid breaching


def isBidBreached():
    if totalBids <= MAX_BIDS:
        return True
    return False

# This function is get random product


def getRandomProduct():
    return random.randint(0, 4)

# This function is to make a bid


def make_a_bid():
    productId = getRandomProduct()
    print(f"Product selected randomly is {PRODUCTS[productId]}")
    if bidWinners[productId] == clientId:
        reason = "ALREADY_CURRENT_WINNER_FOR_RANDOMLY_SELECTED_PRODUCT"
        print(f"[NO BID] with reason: {reason}")
        send(f"NO_BID {reason}")
        return

    currentBid = currentBidAmounts[productId]
    bidAmount = currentBid * (1.0 + (random.randint(5000, 20000) / 100000))

    if bidAmount < clientPresetValue:
        print(
            f"[BID] for product {PRODUCTS[productId]} with amount {bidAmount}")
        send(f"BID {productId} {bidAmount}")
    else:
        reason = "BID_PRCE_IS_HIGHER_THAN_CLIENT_PRESET_PRICE"
        print(f"[NO BID] with reason: {reason}")
        send(f"NO_BID {reason}")
        return

# This function is to handle sever messages


def handle_server():
    global clientId
    global numberOfClients
    global clientPresetValue
    global lastBidBy
    global totalBids
    while True:
        msg = client.recv(4096).decode(FORMAT)
        if len(msg):
            msgList = msg.split()
            msgType = msgList[0]
            if msgType == "CONNECTED":
                clientId = int(msgList[1])
            elif msgType == "PRESET":
                clientPresetValue = float(msgList[1])
            elif msgType == "START_BID":
                bidStartClient = int(msgList[1])
                numberOfClients = int(msgList[2])
                if bidStartClient == clientId:
                    make_a_bid()
                else:
                    lastBidBy = bidStartClient
            elif msgType == "BID":
                lastBidBy = int(msgList[1])
                prodId = int(msgList[2])
                bidAmt = float(msgList[3])
                totalBids += 1
                if lastBidBy == clientId:
                    updateData(lastBidBy, prodId, bidAmt)
                if amIEleigibleClientToBid() and isBidBreached():
                    make_a_bid()
                else:
                    print(
                        f"[BID] from the client {lastBidBy} with amount: {bidAmt} for product {PRODUCTS[prodId]}")
            elif msgType == "NO_BID":
                clientNum = int(msgList[1])
                lastBidBy = clientNum
                msgText = msgList[2]
                if clientNum != clientId:
                    print(
                        f"[NO BID] from the client {clientNum} with reason: {msgText}")
                if amIEleigibleClientToBid() and isBidBreached():
                    make_a_bid()
            elif msgList[0] == "BIDDING_ENDED":
                print("....BIDDING ENDED....")
                return


handle_server()
print("Thank you!!!")
