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

# default values

admin = "Mauch"
bot_nick = 'risu'
default_network = 'bldviz'
default_port = 6667
default_chan = '#risu'
ident = "mauchbot"
realname = "kortana"
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Define  IRC Socket

# initialize one Mensa opject
mensa = Mensa()

############################
#   functions of the bot   #
############################

def connect_network(network_id, port):
    irc.connect((network_id,port)) #Connect to Server
    irc.send('NICK %s\r\n' % bot_nick) #Send our Nick(Notice the Concatenation)
    irc.send('USER %s %s bla :%s\r\n' % (ident, network_id, realname)) #Send User Info to the server
    return irc

def join_channel(channel_name):     
    irc.send('JOIN %s\r\n' % channel_name) 
    return 

def leave_channel(channel_name):    
    irc.send('PART %s\r\n' % channel_name) 
    return 

def disconnect_network():
    irc.send ('QUIT Screw you guys\r\n')
    irc.shutdown(socket.SHUT_RDWR)
    irc.close()

def print_dishes(day, destination): # prints the dishes for the given day to destination
    dishes = mensa.get_dishes(day)
    if dishes == None: # if day was invalid value
        irc.send('PRIVMSG %s :Zu dumm ne Nummer richtig ein zu tippen?\r\n'% (destination))
    else:
        if day != 0: #skip printing of date if today
            irc.send('PRIVMSG %s :%s\r\n'% (destination, dishes[5]))
        irc.send('PRIVMSG %s :D1: %s\r\n'% (destination, dishes[0]))
        irc.send('PRIVMSG %s :D2: %s\r\n' % (destination, dishes[1]))
        irc.send('PRIVMSG %s :E Hauptgerichte: %s, %s \r\n' % (destination, dishes[2], dishes[3]))
        irc.send('PRIVMSG %s :E Beilagen: %s\r\n' % (destination, dishes[4]))

def mensa_search(dish_name, destination): # searches all dishes for the given string and posts it if found 
    searched_dishes = mensa.search_dish(dish_name)
    if searched_dishes == None:
        irc.send('PRIVMSG %s :%s gibt es nicht in den naechsten 3 Wochen\r\n' % (destination, dish_name))
    else:
        for i in range(0, len(searched_dishes)):
            irc.send('PRIVMSG %s :%s\r\n' % (destination, searched_dishes[i]))

def post_say(arg, sender): # takes a string of recievers and sends them the given message
    if not arg.find(":"): # checking for wrong syntax
        irc.send('PRIVMSG %s :Wrong syntax guy\r\n' % (sender))
    else:
        targets = arg.partition(":")[0].split(",")
        message = arg.partition(":")[2]
        for destination in targets: # send message to all destinations
            irc.send('PRIVMSG %s :%s\r\n' % (destination, message))


def post_help(destination, command): #help for all avaiable commands
    if command == "help" or command == "!help":
        irc.send('PRIVMSG %s :Avaiable commands: !mensa, !mensasearch, !say. Type !help "command" for more information\r\n' % (destination)) 
    elif command == "mensa" or command == "!mensa":
        irc.send('PRIVMSG %s :Prints the dishes of a given day. Default day is 0 (today). Syntax: "!mensa d" d between 0 and 14.\r\n' % (destination)) 
    elif command == "mensasearch" or command == "!mensasearch":
        irc.send('PRIVMSG %s :Searches for the given name in dishes of the comming two weeks and prints the date and dish. Syntax: "!mensa_s name" \r\n' % (destination)) 
    elif command == "say" or command == "!say":
        irc.send('PRIVMSG %s :Syntax: "nick1,nick2,#channel1,#channel2:Hello World". Sends to the chosen targets seperated with commas the given string behind :\r\n' % (destination)) 
    else:
        irc.send('PRIVMSG %s :Avaiable commands: !mensa, !mensasearch, !say\r\n' % (destination)) 

# initialice communication

connect_network(default_network, default_port)
join_channel(default_chan)

#######################
#   Main while loop   #
#######################

while True: 
    data = irc.recv(4096) #Make Data the Receive Buffer
    print data #Print the Data to the console(For debug purposes)
    
    if data.find('PING') != -1: #Reply to ping 
        irc.send('PONG ' + data.split()[1] + '\r\n') 
    
    elif data.find('PRIVMSG') != -1: # checking for human communication
        #message = ':'.join(data.split (':')[2:]) #Split the command from the message
        message = data.split (':',2)[2] #Split the message from the data
        destination = data.split()[2]
        user_nick = data.split('!')[0].replace(':','') #The nick of the user issueing the command 
        function = message.split( )[0] #The function is the message split
        if destination == bot_nick:
            destination = user_nick
        arg = None #reset arg for every loop 
        if len(message.split())>1:
            arg = message.split(" ", 1)[1]
        print 'Funtion is ' + function + ' From ' + user_nick #Print who commanded [This is for debug and logging]
        
#################################
#  Parsing of all bot commands  #
#################################

        if (function[0] == "!"):
            
            if function == "!quit" and user_nick == admin: # disconnects the bot from the network
                disconnect_network()
                break
            
            elif function == "!mensa": # posts mensa dishes for given day
                if not arg:
                    print_dishes(0, destination)
                else:
                    print_dishes(int(arg.split()[0]), destination)
            
            elif function == "!mensasearch": #search for a sting in all dishes of the comming two weeks
                if not arg:
                    irc.send('PRIVMSG %s : Musst schon nen Suchbegriff angeben\r\n' % (destination))
                else:
                    mensa_search(arg.split()[0], destination)
            
            elif function == "!help":
                if not arg:
                    post_help(destination,"help")
                else:
                    post_help(destination, arg.split()[0])
            
            elif function == "!say": #post message to list of destinations
                if not arg:
                    irc.send('PRIVMSG %s : ????\r\n' % (destination))
                else:
                    post_say(arg, user_nick)
            
            elif function ==  "!join" and user_nick == admin: #join channel
                channel_name = arg.split()[0] 
                if channel_name[0] != "#":
                    join_channel("#"+channel_name)
                else:
                    join_channel(channel_name)
            
            elif function ==  "!leave" and user_nick == admin: #leave channel
                channel_name = arg.split()[0] 
                if channel_name[0] != "#":
                    leave_channel("#"+channel_name)
                else:
                    leave_channel(channel_name)
            
            else: #print help if unknown command was issued
                irc.send('PRIVMSG %s :unknown command.\r\n' % (destination))
                post_help(destination,"help")
