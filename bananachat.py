import socket
import string
import sys
import json
import random
import requests
from _thread import *

def rollthedice (xdx):
    dicerollsplit = xdx.split("d")
    dicenum = dicerollsplit[0]
    dicenum = int(dicenum)
    diceside = int(dicerollsplit[1])
    rolltotal = int(0)
    rollcount = int(0)
    while rollcount != dicenum:
        datroll = random.randrange(1, diceside)
        rolltotal += datroll
        conn.sendall(str.encode("You rolled: " + str(datroll) + "\r\n"))
        rollcount = rollcount + 1
    return(rolltotal)

def getthemovie (movie):
    # Fetch Movie Data with Full Plot
    apiKey = '&apikey=a21a9d82'
    data_URL = "http://omdbapi.com/?t="
    requestURL = data_URL+movie+apiKey
    OMDBresponse = requests.get(requestURL)
    # If you get a 200 response(success), parse the Json data into a list and then print it to discord.
    if OMDBresponse.status_code == 200:
        jsondata = json.loads(OMDBresponse.text)
        title = 'Title: ' + jsondata['Title']
        year = 'Year: ' + jsondata['Year']
        rated = 'Rated: ' + jsondata['Rated']
        genre = 'Genre: ' + jsondata['Genre']
        actors = 'Actors: ' + jsondata['Actors']
        awards = 'Awards: ' + jsondata['Awards']
        plot = 'Plot: ' + jsondata['Plot']
        #poster = 'Poster: ' + jsondata['Poster']
        #posterpicture = poster.replace('Poster: ', '').strip()
        movielist = [title, year, rated, genre, actors, awards, plot]
    return(movielist)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clients = []
host = ''
port = 23
chat = ""
print("\n"*50)

def threaded_client(conn):
    global chat
    
    conn.send(str.encode("Welcome to the BananaBot!\r\n\r\n"))
    #conn.send(str.encode(chat + "\r"))
    sentex = ""
    msgc = len(clients)
    
    while 1:
        # Did I recieve a valid 2048 bit package?
        try:
            data = conn.recv(2048)
            #print(data)
        except:
            print(data)
        # Can I decode the data recieved as utf-8?
        try:
            reply = data.decode("utf-8")
        except:
            print("Device tried connect with incompatible codec (non-utf8)!")
            conn.send(str.encode("This Device tried connect with incompatible codec (non-utf8)!\r\n"))
            reply = ""
            conn.close()
            clients.remove(conn)
            break
        # If my data is bad then break.
        if not data:
            break
        if data != b'\r\n':
            sentex = sentex + reply
        # Data has passed checks. Move on to decided what to do with data recieved.
        else:
            # Add carriage return after typed command.
            conn.sendall(str.encode("\r\n"))
            # If data is blank then respond with blank.
            if sentex == "":
                sentex = reply
            # /help - print help menu.
            if sentex == "/help":
                conn.sendall(str.encode('/help - list all commands\r\n'  
                '/info - server information and status\r\n'
                '/roll - roll dice. Ex: /roll 2d6\r\n'
                '/movie - get movie info. Ex: /movie The Matrix\r\n'
                '/quit - disconnect from server\r\n'
                '/list - lists all clients connected\r\n\r\n'))
            # /info - print client info.
            elif sentex == "/info":
                for i in clients:
                    if i is not s:
                        msgc = msgc +1
                conn.sendall(str.encode(str(msgc) + " clients online!\r\n"))
            # /client - print client list.
            elif sentex == "/list":
                conn.send(str.encode(str(clients) + "\r\n"))
            # /inventory - print inventory menu.
            elif sentex == "/inventory":
                conn.sendall(str.encode("Inventory Placeholder!"))
            # /roll - check to see if user forgot to specify dice roll.
            elif "/roll" in sentex and "/roll" == sentex:
                conn.sendall(str.encode("Incorrect format. Ex: /roll 2d6\r\n"))
            # /roll - perform dice rolls.
            elif "/roll" in sentex:
                stringsplit = sentex.split(" ")
                xdx = stringsplit[1]
                if xdx == "":
                    conn.sendall(str.encode("Incorrect format. Ex: /roll 2d6\r\n"))
                else:
                    rolltotal = rollthedice(xdx)
                    conn.sendall(str.encode("Your total is: " + str(rolltotal) + "\r\n\r\n"))
            # /banana - prints Hell Yeah!.
            elif sentex == "/banana":
                conn.sendall(str.encode("Hell Yeah!\r\n"))
            # /movie - prints movie data.
            elif "/movie" in sentex:
                movie = sentex.replace('/movie', '').strip()
                movieinfo = getthemovie(movie)
                movieinfojoin = '\r\n'.join(movieinfo)
                conn.sendall(str.encode(movieinfojoin + "\r\n"))
            # /exit - disconnects client.
            elif sentex == "/exit" or sentex == "/quit" or sentex == "/disconnect" or sentex == "/logout" or sentex == "/end":
                conn.sendall(str.encode("Goodbye!\r\n"))
                conn.close()
                clients.remove(conn)
                break
            else:
                for i in clients:
                    if i is not s:
                        # print(clients)
                        try:
                            i.sendall(str.encode(sentex + "\r\n"))
                            msgc = msgc +1
                        except:
                            clients.remove(i)
                            print("Removed the client: " + str(i))
                            msgc = msgc - 1
                chat = chat + sentex + "\r\n"
                print("Sent a message to " + str(msgc) + " clients!")
            msgc = 0
            print(sentex + "\r\n")
            sentex = ""
    conn.close()
    
while 1:
    print("\nTelnet Chat Room! " + host + ":" +str(port))
    if 1:
        while 1:
            try:
                s.bind((host, port))
            except socket.error as e:
                print(str(e))
            s.listen(5)
            print("Waiting for new connections...\r\n")
            
            conn, addr = s.accept()
            print(addr[0] + ":" + str(addr[1]) + " Connected!")
            clients.append(conn)
            start_new_thread(threaded_client,(conn,))