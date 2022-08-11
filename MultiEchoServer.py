from socket import socket, AF_INET, SOCK_STREAM
from select import select
from time import localtime, strftime
from re import sub


"""
by arel shatz and itamar kigis.
the chat requires tkinter to run.
put the chat and the .ico files in the same folder
"""


#convert emoji IDs to printable characters
def ConvertToEmoji(text):
    regex = "((?!\'[\w\s]*){0}(?![\w\s]*\'))"
    for emoji in Emojis:
        text = sub(regex.format("!" + emoji), Emojis[emoji], text)  #replace an emoji ID only if it's not in quotation marks
        
    return text

#send a message to everyone except someone
def SendExcept(response, exception):
    for conn in Connections:
        if conn != exception:
            conn.send(response.encode())

#find the socket (key) by iterating the names (values)
def GetConnByName(name):
    for conn in Connections:
        if Connections[conn][0] == name:
            return conn

#close a connection with a client
def CloseConn(connection):
    wlist.remove(connection)
    CSockets.remove(connection)
    Connections.pop(connection)
    connection.close()    

    if len(CSockets) != 0:
        oldest = CSockets[0]
        if not Connections[oldest][2]:    #if the next user wasn't already an admin
            Connections[oldest][2] = True
            name = Connections[oldest][0]
            response = MsgBlc + Blc + Blc + Blc + name + " is now an admin" + Blc + "#6C6C6C"
            SendExcept(response, None)


#check if user has admin privileges and build error responses
def AdminCheck(user, name):
    conn = None
    response = MsgBlc + Blc + Blc + Blc + "you need admin privileges to access this command" + Blc + "#FF0000"
    if Connections[user][2] == True:
        conn = GetConnByName(name)
        response = MsgBlc + Blc + Blc + Blc + "the user " + name + " does not exist" + Blc + "#FF0000"
    return response, conn

#check if the given name is valid
def NameCheck(name):
    if name.find(" ") == -1 and name.find("(admin)") == -1:    #check if the name doesn't contain a space, a fake admin tag or a fake private tag
        conn = GetConnByName(name)
        return conn == None
        
    return False



"""user commands handling"""

#instead of having multiple functions that do the same thing
def commandHandler(senderName, args, succResponse, failResponse, attr, newAttrState, needAdmin):
    if needAdmin:
        nameToOperate = args[0]
        output, conn = AdminCheck(current_socket, nameToOperate)
    else:
        conn = current_socket
        
    if conn:
        if Connections[conn][attr] == newAttrState:
            current_socket.send(failResponse.encode())
        else:
            Connections[conn][attr] = newAttrState
            SendExcept(succResponse, None)
    else:
        current_socket.send(output.encode())

 
def Emoji(senderName, args, response):
    text = "type ![emoji] to print an emoji.\ntyping '![emoji]' will cancel the emoji.\n\n"
    for emoji in Emojis:
        text += "!" + emoji + " - " + Emojis[emoji] + "\n"
        
    response = MsgBlc + Blc + Blc + Blc + text + Blc + "#6C6C6C"
    current_socket.send(response.encode())

    
def Help(senderName, args, response):
    helpText = ("commands:\n\n"
    "/help - get commnads information\n"
    "/emoji - view available emojis\n"
    "/quit - exit from the chat\n"
    "/rename [new name] - change your name\n"
    "/promote [name] - give someone owner privileges (requires admin privileges)\n"
    "/demote [name] - take away someone's owner privileges (requires admin privileges)\n"
    "/kick [name] - kick someone from the chat (requires admin privileges)\n"
    "/mute [name] - make someone unable to speak (requires admin privileges)\n"
    "/unmute [name] - make someone able to speak (requires admin privileges)\n"
    "/p [name] [message] - send a private message to someone\n"
    "/list - get a list of all connected client names\n")

    response = MsgBlc + Blc + Blc + Blc + helpText + Blc + "#6C6C6C"
    current_socket.send(response.encode())


def Quit(senderName, args, response):
    ExitType(None, response)


def Rename(senderName, args, response):
    NewName = " ".join(args)
    failResponse = MsgBlc + Blc + Blc + Blc + "you already had the name" + NewName + NewName + Blc + "#FF0000"
    succResponse = response + Blc + Blc + senderName + " changed his name to " + NewName + Blc + "#6C6C6C"
    IsValid = NameCheck(NewName)
    if IsValid:
        commandHandler(senderName, args, succResponse, failResponse, 0, NewName, False)
    else:
        output = MsgBlc + Blc + Blc + Blc + NewName + " already exists" + Blc + "#FF0000"
        current_socket.send(output.encode())


def Promote(senderName, args, response):
    nameToPromote = args[0]
    failResponse = MsgBlc + Blc + Blc + Blc + nameToPromote + " already has permissions" + Blc + "#FF0000"
    succResponse = response + Blc + Blc + nameToPromote + " was promoted by " + senderName + Blc + "#6C6C6C"
    commandHandler(senderName, args, succResponse, failResponse, 2, True, True)


def Demote(senderName, args, response):
    nameToDemote = args[0]
    failResponse = MsgBlc + Blc + Blc + Blc + nameToDemote + " alredy had no permissions" + Blc + "#FF0000"
    succResponse = response + Blc + Blc + nameToDemote + " was demoted by " + senderName + Blc + "#6C6C6C"
    commandHandler(senderName, args, succResponse, failResponse, 2, False, True)


def Kick(senderName, args, response):
    nameToKick = args[0]
    output, conn = AdminCheck(current_socket, nameToKick)
    if conn:
        conn.send("1".encode())
        CloseConn(conn)
        response += Blc + Blc + nameToKick + " was kicked from the chat by " + senderName + Blc + "#6C6C6C"
        SendExcept(response, None)
    else:
        current_socket.send(output.encode())


def Private(senderName, args, response):
    ToName = args[0]
    color = Connections[current_socket][1]
    conn = GetConnByName(ToName)
    if conn:
        message = " ".join(args[1:])
        message = ConvertToEmoji(message)
        response += senderName + " --> " + ToName + ": " + Blc + color + Blc + message + Blc + "#FFA400"
        conn.send(response.encode())
    else:
        response = MsgBlc + Blc + Blc + Blc + "the user " + ToName + " does not exist" + Blc + "#FF0000"
        
    current_socket.send(response.encode())


def Mute(senderName, args, response):
    nameToMute = args[0]
    failResponse = MsgBlc + Blc + Blc + Blc + nameToMute + " was already muted" + Blc + "#FF0000"
    succResponse = response + Blc + Blc + nameToMute + " was muted by " + senderName + Blc + "#6C6C6C"
    commandHandler(senderName, args, succResponse, failResponse, 3, True, True)


def Unmute(senderName, args, response):
    nameToUnmute = args[0]
    failResponse = MsgBlc + Blc + Blc + Blc + nameToUnmute + " was already not muted" + Blc + "#FF0000"
    succResponse = response + Blc + Blc + nameToUnmute + " was unmuted by " + senderName + Blc + "#6C6C6C"
    commandHandler(senderName, args, succResponse, failResponse, 3, False, True)


def List(senderName, args, response):
    MsgBody = ""
    for connected in Connections:
        MsgBody += Connections[connected][0] + "\n"
    response = MsgBlc + Blc + Blc + Blc + "currently connected:\n" + MsgBody + Blc + "#6C6C6C"
    current_socket.send(response.encode())



"""data type handling"""

#if the user sent a name request
def NameType(name, response):
    IsValidName = NameCheck(name)
    if IsValidName:
        current_socket.send("1".encode())   #acknowledgment that the name is valid
        color = colors[len(CSockets) - 1 % len(colors)]
        owner = False
        muted = False
        Connections[current_socket] = [name, color, owner, muted]
        Connections[CSockets[0]][2] = True
        response += Blc + Blc + name + " has joined the chat" + Blc + "#6C6C6C"
        SendExcept(response, current_socket)
                    
    else:
        current_socket.send("0".encode())   #acknowledgment that the name is invalid

#if the user wants to exit
def ExitType(data, response):
    try:
        name = Connections[current_socket][0]
    except:
        #if the client is not yet in the chat
        CSockets.remove(connection)
        return
    
    response += Blc + Blc + name + " has left the chat" + Blc + "#6C6C6C"
    SendExcept(response, current_socket)
    CloseConn(current_socket)

#if the user sent a command
def CommandType(data, response):
    command = data[1:]
    cmd = command.split(" ")
    op = cmd[0]
    args = cmd[1:]
    senderName = Connections[current_socket][0]
    try:
        Commands[op](senderName, args, response)
    except KeyError:
        #if command doesn't exist
        response = MsgBlc + Blc + Blc + Blc + "invalid syntax - type /help for more information" + Blc + "#FF0000"
        current_socket.send(response.encode())

#if the user sent plain text
def MessageType(data, response):
    if Connections[current_socket][3] == False: #if user is not muted

        senderName = Connections[current_socket][0]
        if Connections[current_socket][2] == True:   #add an exclusive admin tag to admins only
            senderName += " (admin)"

        color = Connections[current_socket][1]
        response += senderName + ": " + Blc + color + Blc + data + Blc + "#000000"
        response = ConvertToEmoji(response)
        SendExcept(response, None)
    else:
        response = MsgBlc + Blc + Blc + Blc + "you are muted, you can't speak here" + Blc + "#FF0000"
        current_socket.send(response.encode())



#define variables and create the server
Emojis = {
    "grin": "\U0001F600",
    "laugh": "\U0001F923",
    "smile": "\U0001F642",
    "wink": "\U0001F609",
    "angry": "\U0001F620",
    "sad": "\U0001F622",
    "surprised": "\U0001F62E",
    "neutual": "\U0001F610",
    "whatever": "\U0001F644"
    }

Commands = {
    "emoji": Emoji,
    "help": Help,
    "quit": Quit,
    "rename": Rename,
    "promote": Promote,
    "demote": Demote,
    "kick": Kick,
    "p": Private,
    "mute": Mute,
    "unmute": Unmute,
    "list": List
    }

Types = {
    "0": NameType,
    "1": ExitType,
    "2": CommandType,
    "3": MessageType
    }


Blc = chr(999999)       #to understand where the end of every msg attribute is
MsgBlc = chr(999998)    #to understand where the end of every msg is (if multiple messages are sent)
Connections = {}
colors = ["#FF0000", "#00CC00", "#0000FF", "#FF00FF", "#00FFFF", "#8900FF", "#FF8B00"]
num_of_connections = 0

ip = "localhost"
port = 12345

SSocket = socket(AF_INET, SOCK_STREAM)
SSocket.bind((ip, port))
SSocket.listen()
CSockets = []


#get incoming connections and messages
while True:
    rlist, wlist, xlist = select([SSocket] + CSockets, CSockets, [])
    for current_socket in rlist:
        if current_socket is SSocket:
            connection, client_address = current_socket.accept()
            CSockets.append(connection)
        else:
            data = current_socket.recv(1024).decode()
            if data:
                currentTime = localtime()
                HoursMinutes = strftime("%H:%M", currentTime)
                response = MsgBlc + HoursMinutes + " " + Blc
                type = data[0]
                data = data[1:]

                Types[type](data, response)
