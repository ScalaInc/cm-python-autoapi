import json,os
import urllib2, httplib
import datetime
import time
import platform
import re
import urllib
import random, string
import socket
import getpass
import win32api
import win32net
import win32con
import win32netcon
import time

print ("posting to HTTP:")

def log_in(username,password):
    global server
    try:
        #Object for LOG IN
        params = {"username": username,
                  "password": password
                  }

        #Prepare URL with a suitable timeout
        req = urllib2.Request(server+'/ContentManager/api/rest/auth/login')
        urllib2.timeout = 2000

        #Add Headers
        req.method = "POST"
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept-Encoding', 'gzip,deflate')

        #Get Reply and look for API TOKEN
        response = urllib2.urlopen(req, json.dumps(params))
        data = json.load(response)
        #print data['apiToken']

        #Check Reply
        if response.getcode() == 200: 
            return data['apiToken']
        else:
            print ("Login fail" + response.getcode())
            return "failed" 
    except:
        return "failed"

def Scala_Query(url_request):
    global token
    #Prepare URL with a suitable timeout    
    #print server+'/ContentManager/api/rest/' + url_request

    req = urllib2.Request( server+'/ContentManager/api/rest/' + url_request )
    urllib2.timeout = 5000

    #Add Headers
    req.method = "GET"
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept-Encoding', 'gzip,deflate')
    req.add_header('apiToken', token);

    #Get Reply
    response = urllib2.urlopen(req)
    data = json.load(response)  

    #Check Reply
    if response.getcode() == 200: 
        return data
    else:
        print ("Login fail" + response.getcode())
        return ""


def Scala_Playlist_Query(playlist): 

    fields = urllib.quote("{'name' : {'values':['%"+ playlist + "%'], comparator : 'like'}}")

    my_url = "playlists/all?limit=1000&offset=0&sort=name&filters=" + fields + "&fields=id,name"

    myobject = Scala_Query(my_url)

    #{'name' : {'values':['Argos Inspire Bay Old Street'], comparator : 'eq'}}

    return myobject

time1 = time.time()

server   = "https://hrgcm.pixelinspiration.co.uk"
username = "administrator"
password = "y884ptfgy61rvu"
token    = log_in(username,password)

if token != "failed" :
    #Perform Query
    playlist = ""
    myresult = Scala_Playlist_Query(playlist)
    
    time2 = time.time()
    print (time2 - time1) * 1000
    for match in myresult['list']:
        print "   " + str(match)#['name']
