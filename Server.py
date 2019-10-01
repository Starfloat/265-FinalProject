import socket
import time
from threading import Thread

host = '192.168.1.3'
port = 33000
address = (host, port)
clients = {}
key = 'A8c#K&k35J$lw*' # Encryption key for now

# Dictionaries for use with encryption/decryption
numbers = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8, "J": 9,
               "K": 10, "L": 11, "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17, "S": 18,
               "T": 19, "U": 20, "V": 21, "W": 22, "X": 23, "Y": 24, "Z": 25, "a": 26, "b": 27,
               "c": 28, "d": 29, "e": 30, "f": 31, "g": 32, "h": 33, "i": 34, "j": 35, "k": 36,
               "l": 37, "m": 38, "n": 39, "o": 40, "p": 41, "q": 42, "r": 43, "s": 44, "t": 45,
               "u": 46, "v": 47, "w": 48, "x": 49, "y": 50, "z": 51, ",": 52, ".": 53, "/": 54,
               "<": 55, ">": 56, "?": 57, ";": 58, "'": 59, ":": 60, '"': 61, "[": 62, "]": 63,
               "{": 64, "}": 65, "!": 66, "@": 67, "#": 68, "$": 69, "%": 70, "^": 71, "&": 72,
               "*": 73, "(": 74, ")": 75, "-": 76, "=": 77, "_": 78, "+": 79, "0": 80, "1": 81,
               "2": 82, "3": 83, "4": 84, "5": 85, "6": 86, "7": 87, "8": 88, "9": 89, " ": 90}

letters = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H", 8: "I", 9: "J",
               10: "K", 11: "L", 12: "M", 13: "N", 14: "O", 15: "P", 16: "Q", 17: "R", 18: "S",
               19: "T", 20: "U", 21: "V", 22: "W", 23: "X", 24: "Y", 25: "Z", 26: "a", 27: "b",
               28: "c", 29: "d", 30: "e", 31: "f", 32: "g", 33: "h", 34: "i", 35: "j", 36: "k",
               37: "l", 38: "m", 39: "n", 40: "o", 41: "p", 42: "q", 43: "r", 44: "s", 45: "t",
               46: "u", 47: "v", 48: "w", 49: "x", 50: "y", 51: "z", 52: ",", 53: ".", 54: "/",
               55: "<", 56: ">", 57: "?", 58: ";", 59: "'", 60: ":", 61: '"', 62: "[", 63: "]",
               64: "{", 65: "}", 66: "!", 67: "@", 68: "#", 69: "$", 70: "%", 71: "^", 72: "&",
               73: "*", 74: "(", 75: ")", 76: "-", 77: "=", 78: "_", 79: "+", 80: "0", 81: "1",
               82: "2", 83: "3", 84: "4", 85: "5", 86: "6", 87: "7", 88: "8", 89: "9", 90: " "}


# Started in Main(), infinite loop waiting for new connections
# On connection, starts a new thread for each client
def connections(server):
    while True:
        client, addr = server.accept()
        welcome = encrypt("Hello! Please enter a username.")
        client.send(welcome.encode())
        client_thread = Thread(target=manage, args=(client,))
        client_thread.start()


# Loops through the sockets we've been saving in clients dictionary
def echo_msg(name, msg):
    encrypt_msg = encrypt(time.strftime('[%H:%M] ') + name + ': ' + msg)
    try:
        for client in clients:
            client.send(bytes(encrypt_msg, "utf8"))
    except ConnectionResetError:
        pass


# This is like above but without the name: in the msg,
# just an easy way of handling joining and leaving msgs
def echo_msg_alt(msg):
    try:
        for client in clients:
            client.send(bytes(encrypt(msg), "utf8"))
    except ConnectionResetError or ConnectionAbortedError:
        pass


# Actually sends a string of the names in clients dictionary
# Used to update the list that shows who's online
# the string starts with a protocol marker %%NAMELIST%%
# Checked on the clients side when receiving messages
def send_names():
    names = ''
    for keys in clients:
        names += ',' + clients.get(keys)
    try:
        for client in clients:
            client.send(bytes(encrypt("%%NAMELIST%% "+names), "utf8"))
    except ConnectionResetError or ConnectionAbortedError:
        pass
    return


# First gets the name after connections() asks for it
# Then waits for messages and calls echo_msg to display them
def manage(client):
    encrypt_name = client.recv(1024).decode()
    name = decrypt(encrypt_name)
    clients[client] = name
    send_names()
    echo_msg_alt((time.strftime('[%H:%M] ') + "User "+name+" has joined!"))
    try:
        while True:
            encrypt_msg = client.recv(1024).decode()
            msg = decrypt(encrypt_msg)
            echo_msg(name, msg)
    except ConnectionError: # If a client quits
        print("Client left")
        echo_msg_alt(name+" has left the chat.")
        clients.pop(client)
        send_names()
        client.close()


# Encryption function
def encrypt(plaintext):
    keyStr = ''
    ciphertext = ''

    # Makes keyStr by repeating 'key', makes it a little longer than plaintext to avoid problems
    for i in range((len(plaintext) // len(key)) + 1):
        keyStr += key

    sizePlain = len(plaintext)
    sizeKeyStr = len(keyStr)

    # Shortens keyStr to be the same size as plaintext
    keyStr = keyStr[:-(sizeKeyStr - sizePlain)]

    # Makes ciphertext. Uses numbers dict to get values of the two letters, Shift = (A + B) % 26
    # Then uses shift to get new letter from letters dict, concatenates that on the end of ciphertext
    try:
        for i in range(sizePlain):
            ciphertext += letters.get((numbers.get(plaintext[i]) + numbers.get(keyStr[i])) % 91)
    except TypeError:
        pass
    return ciphertext

# Decryption Function
def decrypt(txt):
    keyStr = ''
    decryption = ''
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                'U',
                'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                'p',
                'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ',', '.', '/', '<', '>', '?', ';', "'", ':', '"',
                '[',
                ']', '{', '}', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+', '0', '1', '2',
                '3',
                '4', '5', '6', '7', '8', '9', ' ']

    # Makes keyStr by repeating 'key', makes it a little longer than plaintext to avoid problems
    for i in range((len(txt) // len(key)) + 1):
        keyStr += key

    sizeTxt = len(txt)
    sizeKeyStr = len(keyStr)

    # Shortens keyStr to be the same size as plaintxt
    keyStr = keyStr[:-(sizeKeyStr - sizeTxt)]

    #
    for i in range(sizeTxt):
        try:
            if numbers.get(txt[i]) >= numbers.get(keyStr[i]):
                decryption += letters.get(numbers.get(txt[i]) - numbers.get(keyStr[i]))
            else:
                decryption += alphabet[-(numbers.get(keyStr[i]) - numbers.get(txt[i]))]
        except TypeError:
            pass
    return decryption



def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(10)
    print("Server Ready")
    connections(server)


main()
