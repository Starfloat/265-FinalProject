import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.ttk as ttk  # Tk themed widgets
import socket
import subprocess
import os
from threading import Thread


class Window(tk.Tk): # (tk.Tk) inheritance
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("Chat Program")
        self.menu = tk.Menu()
        
        # //////////////////Initialize Frames///////////////////////// #
        
        # Main container, frame created for menu
        mainFrame = tk.Frame(self)

        # bottom frame for inputting messages, buttons
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=0)

        # left frame to handle message area
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # right frame for user online list & scrollbar
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.LEFT, fill=tk.X)

        # //////////////// Inserting Widgets to Frames /////////////////////// #

        # Online/Friend List Box
        self.friendlist_box = tk.Listbox(self.left_frame, width=15)
        self.friendlist_box.pack(side=tk.RIGHT, fill=tk.Y)

        # scrollbar
        self.scroll_bar = tk.Scrollbar(self.left_frame, orient='vertical')
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # the chat box to display messages
        self.chat_box = tk.Text(self.left_frame, bg="white", fg="black", wrap=tk.WORD, width=30)
        self.chat_box.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        self.chat_box['yscrollcommand'] = self.scroll_bar.set
        self.chat_box.insert(tk.END, "Welcome to Chat Program\n")
        self.chat_box.configure(state='disabled')


        # message box to input message
        self.msg_box = tk.Entry(self.bottom_frame)
        self.msg_box.pack(side=tk.LEFT, expand=1, fill=tk.X, padx=5, pady=5)
        self.msg_box.bind("<Return>", self.send_msg)
        self.msg_box.focus()

        # send button
        send_button = tk.Button(self.bottom_frame, text="SEND", command=self.send_msg)
        send_button.pack(side=tk.RIGHT, expand=0, padx=(5), pady=(5))

        # Cascading menus
        menubar = tk.Menu(mainFrame)
        
        menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Quit", command=self.quit)

        helpmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="User Manual", command=self.openManual)
        helpmenu.add_command(label="About", command=self.about)

        tk.Tk.config(self, menu=menubar)


        # /////////////////////// Functions /////////////////////// #


    def enter_key(self):
        self.enter("<Return>", self.send_msg)
        self.msg_box.bind("<Return>", self.msg_box)

    # Sends message on button click
    def send_msg(self, event = None):
        msg = self.msg_box.get()
        encrypt_msg = self.encrypt(msg)
        client.send(bytes(encrypt_msg, 'utf8'))
        self.msg_box.delete(0, 'end')

    def encrypt(self, plaintext):
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

    def openManual(self):
        if os.name == 'nt': # windows 
            os.startfile('manual.pdf')
        elif os.name == 'posix': # linux, mac
            subprocess.call(('manual.pdf'))
        
    def about(self):
        message = "CSC 265-02 Project\n  Chat Program\n  Sunni Lakhaisy\n   Zach Sturgill"
        msgbox.showinfo("About", message)

    def quit(self):
        if msgbox.askyesno("Exit Program", "Do you want to exit this program?"):
            message = "Chat Program exiting..."
            msgbox.showinfo("Window Closing", message)
            client.close()
            self.after(1500, self.destroy)

# The thread in main starts this method which gets/displays incoming messages
    def receive_msg(self):
        try:
            while True:
                encrypt_msg = client.recv(1024).decode()
                msg = self.decrypt(encrypt_msg)
                if "%%NAMELIST%%" in msg:
                    self.update_names(msg)
                else:
                    self.chat_box.configure(state="normal")
                    self.chat_box.insert(tk.END, msg+"\n\n")
                    self.chat_box.configure(state="disabled")
                    self.chat_box.see(tk.END)
        except ConnectionAbortedError:
            pass


    def update_names(self,names):
        name_list = names.split(',')
        name_list.pop(0)
        self.friendlist_box.delete(0, tk.END)
        for i in range(len(name_list)):
            self.friendlist_box.insert(i, name_list[i])

    def decrypt(self, txt):
        keyStr = ''
        decryption = ''
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ',', '.', '/', '<', '>', '?', ';', "'", ':',
                    '"', '[', ']', '{', '}', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+', '0', '1',
                    '2', '3', '4', '5', '6', '7', '8', '9', ' ']

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


if __name__ == "__main__":
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
    key = "A8c#K&k35J$lw*"
    host = "192.168.1.3"
    port = 33000
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))    # Gets connection here
    mainwindow = Window()
    mainwindow.geometry('640x480')
    mainwindow.minsize(640, 480)
    receive = Thread(target=mainwindow.receive_msg)
    receive.start() # Starts receive method
    mainwindow.mainloop()
