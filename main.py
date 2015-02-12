#!/usr/bin/env python

import socket
import time
from lxml import html
import requests
import re
from classes import * 
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

admin = "Mauch"
bot_nick = 'risu'
default_network = 'bldviz'
default_port = 6667
default_chan = '#risu'
ident = "mauchbot"
realname = "kortana"
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Define  IRC Socket

mensa = Mensa()


def connect_network(network_id, port):
    irc.connect((network_id,port)) #Connect to Server
    irc.send('NICK %s\r\n' % bot_nick) #Send our Nick(Notice the Concatenation)
    irc.send('USER %s %s bla :%s\r\n' % (ident, network_id, realname)) #Send User Info to the server
    return irc

def join_channel(channel_name):    
    irc.send('JOIN %s\r\n' % channel_name) # Join the pre defined channel
    return 

def leave_channel(channel_name):    
    irc.send('PART %s\r\n' % channel_name) # Join the pre defined channel
    return 

def disconnect_network():
    irc.send ('QUIT Screw you guys\r\n')
    irc.shutdown(socket.SHUT_RDWR)
    irc.close()


def alles_dreck(channel_name):
    page = requests.get("http://rolf-schneider.net/mensa/?translation=reality")
    tree = html.fromstring(page.text)
    meal = tree.xpath("//td[@id='meal']/text()")
    irc.send('PRIVMSG %s :D1: %s\r\n' % (channel_name, meal[2]))
    irc.send('PRIVMSG %s :D2: %s\r\n' % (channel_name, meal[3]))
    irc.send('PRIVMSG %s :E:%s, %s \r\n' % (channel_name, meal[5], meal[6]))
    irc.send('PRIVMSG %s :E beilagen: %s, %s, %s, %s\r\n' % (channel_name, meal[7], meal[8], meal[9], meal[10]))
    return

def print_dishes(day, destination):
    dishes = mensa.get_dishes(day)
    if dishes == None:
        irc.send('PRIVMSG %s :Zu dumm ne Nummer richtig ein zu tippen?\r\n'% (destination))
    else:
        irc.send('PRIVMSG %s :%s\r\n'% (destination, dishes[5]))
        irc.send('PRIVMSG %s :D1: %s\r\n'% (destination, dishes[0]))
        irc.send('PRIVMSG %s :D2: %s\r\n' % (destination, dishes[1]))
        irc.send('PRIVMSG %s :E Hauptgerichte: %s, %s \r\n' % (destination, dishes[2], dishes[3]))
        irc.send('PRIVMSG %s :E Beilagen: %s\r\n' % (destination, dishes[4]))

def mensa_search(dish_name, destination):
    searched_dishes = mensa.search_dish(dish_name)
    if searched_dishes == None:
        irc.send('PRIVMSG %s :%s gibt es nicht in den naechsten 3 Wochen\r\n' % (destination, dish_name))
    else:
        for i in range(0, len(searched_dishes)):
            irc.send('PRIVMSG %s :%s\r\n' % (destination, searched_dishes[i]))

def post_say(arg, sender):
    if not arg.find(":"):
        irc.send('PRIVMSG %s :Wrong syntax guy\r\n' % (sender))
    else:
        targets = arg.partition(":")[0].split(",")
        message = arg.partition(":")[2]
        for destination in targets:
            irc.send('PRIVMSG %s :%s\r\n' % (destination, message))


def post_help(destination, command):
    if command == "help" or command == "!help":
        irc.send('PRIVMSG %s :Avaiable commands: !mensa, !mensa_s, !say. Type !help "command" for more information\r\n' % (destination)) 
    elif command == "mensa" or command == "!mensa":
        irc.send('PRIVMSG %s :Prints the dishes of a given day. Default day is 0 (today). Syntax: "!mensa d" d between 0 and 14.\r\n' % (destination)) 
    elif command == "mensa_s" or command == "!mensa_s":
        irc.send('PRIVMSG %s :Searches for the given name in dishes of the comming two weeks and prints the date and dish. Syntax: "!mensa_s name" \r\n' % (destination)) 
    elif command == "say" or command == "!say":
        irc.send('PRIVMSG %s :Syntax: "nick1,nick2,#channel1,#channel2:Hello World". Sends to the chosen targets seperated with commas the given string behind :\r\n' % (destination)) 
    else:
        irc.send('PRIVMSG %s :Avaiable commands: !mensa, !mensa_s, !say\r\n' % (destination)) 

connect_network(default_network, default_port)
join_channel(default_chan)

while True: #While Connection is Active
    data = irc.recv(4096) #Make Data the Receive Buffer
    print data #Print the Data to the console(For debug purposes)
    if data.find('PING') != -1: #If PING is Found in the Data
        irc.send('PONG ' + data.split()[1] + '\r\n') #Send back a PONG

    elif data.find('PRIVMSG') != -1: #IF PRIVMSG is in the Data Parse it
        message = ':'.join(data.split (':')[2:]) #Split the command from the message
        destination = data.split()[2]
        user_nick = data.split('!')[ 0 ].replace(':','') #The nick of the user issueing the command is taken from the hostname
        function = message.split( )[0] #The function is the message split
        arg = None
        if destination == bot_nick:
            destination = user_nick
        if len(message.split())>1:
            arg = message.split(" ", 1)[1]
        print 'Funtion is ' + function + ' From ' + user_nick #Print who commanded [This is for debug and logging]
        if (function[0] == "!"):
            if function == "!quit" and user_nick == admin:
                disconnect_network()
                break
            if function == "!mensa":
                if not arg:
                    print_dishes(0, destination)
                else:
                    print_dishes(int(arg.split()[0]), destination)
            if function == "!mensa_s":
                if not arg:
                    irc.send('PRIVMSG %s : Musst schon nen Suchbegriff angeben\r\n' % (destination))
                else:
                    mensa_search(arg.split()[0], destination)
            
            if function == "!help":
                if not arg:
                    post_help(destination,"help")
                else:
                    post_help(destination, arg.split()[0])
            if function == "!say":
                if not arg:
                    irc.send('PRIVMSG %s : ????\r\n' % (destination))
                else:
                    post_say(arg, user_nick)
            if function ==  "!join" and user_nick == admin:
                channel_name = arg.split()[0] 
                if channel_name[0] != "#":
                    join_channel("#"+channel_name)
                else:
                    join_channel(channel_name)
            if function ==  "!leave" and user_nick == admin:
                channel_name = arg.split()[0] 
                if channel_name[0] != "#":
                    leave_channel("#"+channel_name)
                else:
                    leave_channel(channel_name)
