from tkinter import Tk, Frame, Button, BOTTOM, X, Label, TOP, StringVar, Entry, DISABLED, NORMAL, BOTH, LEFT, Text, INSERT
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from sys import exit as sysExit


"""
by arel shatz and itamar kigis.
the chat requires tkinter to run.
put the chat and the .ico files in the same folder
"""


class Window():    
    def __init__(self, root, title, icon, IsClient):
        self.running = True
        self.line = 1
        self.is_client = IsClient
        self.msg = ""
        self.root = root
        self.root.title(title)
        self.root.iconbitmap(icon)

        self.root.protocol("WM_DELETE_WINDOW", self.Exit)   #bind the 'x' button to exiting
        
        self.frame = Frame(self.root)
        self.frame.pack()

        #declare fonts
        self.DefaultFont = ("Helvetica", 10, "bold")
        self.INPFont = ("Helvetica", 14)

        #activate the "EnableSend" function when the user writes or deletes a character
        self.input = StringVar()
        self.input.trace("w", self.EnableSend)
        
        #create wigets to perform operations
        self.INPBox = Entry(self.root, textvariable=self.input, font=self.INPFont)
        self.ExitB = Button(self.root, text = "Exit", command=self.Exit, font=self.DefaultFont)
        self.SendB = Button(self.root, text = "Send", command=self.GetMsg, font=self.DefaultFont, state=DISABLED)

        #align wigets on the window
        self.INPBox.pack(side = TOP, expand=True, fill=BOTH)
        self.ExitB.pack(side = LEFT, expand=True, fill=X)
        self.SendB.pack(side = LEFT, expand=True, fill=X)

        self.root.bind('<Return>', self.GetMsg) #bind the "Enter" key to the message sender

        self.root.lift()    #bring the window to the front of the screen
        
    #make the "send" button pressable when a msg is written
    def EnableSend(self, *args):
        if len(self.input.get()) == 0:
            self.SendB.config(state=DISABLED)
        else:
            self.SendB.config(state=NORMAL)
            
    #destroys the connection and the window
    def Exit(self):
        self.running = False
        self.root.destroy()
        if self.is_client:
            Send(exitType)
            self.is_client = False

    #copy the text in the entry wiget and erase it
    def GetMsg(self, *args):
        self.msg = self.input.get()
        self.input.set("")

        
    #handles input from user and output from server without blocking
    def I_O(self):
        while self.running:
            
            self.root.update()  #updates tkinter wigets

            if self.msg:    #if a msg was grabbed with the GetMsg function
                msg = self.msg
                self.msg = ""
                return msg

            if self.is_client:
                
                rlist, wlist, xlist = select([CSocket], [CSocket], [])
                if rlist:
                    response = CSocket.recv(1024).decode()
                    
                    if response == "1": #if the user is getting kicked
                        self.Exit()

                    else:
                        response = response[1:] #remove the first message blocker
                        messages = response.split(MsgBlc)   #to handle a lot of messages at once
                    
                        for message in messages:
                            elements = message.split(Blc)
                            time, name, nameColor, text, textColor = elements

                            #find the correct indexes for colors
                            self.line += 1
                            line = str(self.line)
                            row = 0
                        
                            timeStart = line + "." + str(row)
                            row += len(time)
                            timeEnd = line + "." + str(row)

                            NameStart = timeEnd
                            row += len(name)
                            NameEnd = line + "." + str(row)

                            TextStart = NameEnd
                            row += len(text)
                            TextEnd = line + "." + str(row)
                            nameTag = "N" + line
                            textTag = "T" + line

                            #add the line skips in the msg
                            lineSkips = text.count("\n")
                            self.line += lineSkips
                        
                            textBox.tag_configure(nameTag, foreground=nameColor)
                            textBox.tag_configure(textTag, foreground=textColor)

                            #add colors
                            textBox.config(state=NORMAL)
                            textBox.tag_add("time", timeStart, timeEnd)
                            textBox.tag_add(nameTag, NameStart, NameEnd)
                            textBox.tag_add(textTag, TextStart, TextEnd)

                            #insert text
                            textBox.insert(timeStart, time, "time")
                            textBox.insert(NameStart, name, nameTag)
                            textBox.insert(TextStart, text + "\n", textTag)
                            textBox.config(state=DISABLED)
                        
                            textBox.see("end")  #auto scroll to the end of the page
                    
#send msg to the server
def Send(msg):
    try:
        CSocket.send(msg.encode())
    except:
        pass


#try to connect to the server
def Connect():
    global connected
    try:
        CSocket.connect((ip, port))
        connected = True
        root.destroy()
    except:
        connError.config(text="failed to connect")


nameType = "0"
exitType = "1"
commandType = "2"
messageType = "3"
Blc = chr(999999)       #to understand where the end of every msg attribute is
MsgBlc = chr(999998)    #to understand where the end of every msg is (if multiple messages are sent)


while True:
    #establish connection
    ip = "localhost"
    port = 12345
    CSocket = socket(AF_INET, SOCK_STREAM)
    SSocket = []
    connected = False
    
    #create the connection window
    root = Tk()
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.title("connecting")
    root.iconbitmap("gears.ico")
    frame = Frame(root)
    frame.pack()
    DefaultFont = ("Ariel", 13)
    Button(root, text = "Connect", command=Connect, font=DefaultFont).pack(side=BOTTOM, expand=True, fill=X)
    connError = Label(root, text="", fg="#FF0000", font=DefaultFont)
    connError.pack(side=TOP, expand=True, fill=X)

    root.mainloop()

    if not connected:
        sysExit()


    #create the name input window and send the input to the server
    NameRoot = Tk()
    Label(NameRoot, text="Enter Your Name", font=("Ariel", 18, "bold")).pack(side = TOP, expand=True, fill=X)
    errorMsg = Label(NameRoot, text="", fg="red", font=("Ariel", 11))
    errorMsg.pack(side = TOP, expand=True, fill=X)
    NameWin = Window(NameRoot, "name", "gears.ico", False)

    nameExists = False

    #infinite loop until the user enters a valid name
    while not nameExists:
        name = NameWin.I_O()
        if name:
            nameMsg = nameType + name
            Send(nameMsg)
            nameResponse = CSocket.recv(1024).decode()
            if nameResponse == "1": #name is valid
                nameExists = True
                chatExists = True
                NameWin.Exit()
        
            else:
                errorMsg.configure(text = "name is invalid")

        else:
            Send(exitType)
            chatExists = False
            nameExists = True


    if not chatExists:  #go back to the connection window on exit
        continue
    
    #create chat window and send input to server
    ChatRoot = Tk()
    textBox = Text(ChatRoot, state=NORMAL,font=("Helvetica", 14))
    textBox.pack(side = TOP, expand=True, fill=BOTH)
    textBox.insert(INSERT, "type /help for more information" + "\n")
    textBox.config(state=DISABLED)
    textBox.tag_configure("time", foreground="#6C6C6C")
    ChatWin = Window(ChatRoot, "chat", "chat.ico", True)

    while chatExists:
        msg = ChatWin.I_O()
        if msg:
            if msg[0] == "/":
                if msg == "/quit":  #go back to the connection window on exit
                    ChatWin.Exit()
                    chatExists = False
                    continue
                else:
                    data = commandType + msg
        
            else:
                data = messageType + msg
        
            Send(data)

        else:
            chatExists = False  #go back to the connection window on exit
            continue

    
