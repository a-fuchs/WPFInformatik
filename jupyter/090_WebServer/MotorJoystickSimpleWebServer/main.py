#######################################
# Constants


#======================================
SSID        = "ESP minimal http-server"
PASSWORD    = '123123123123' # default is 'micropythoN', attension: at least 8 chars, otherwise error: 'OSError: can't set AP config'
MAX_CLIENTS = 5 # Good maximal ammount of posiible clients


POLL_TIME_MILLIS = 0

#######################################
# Init

#======================================
# Typical code for setting up the controller as access point.
# At the end we get a server-socket listening for clients to connect:

import network
import socket # usocket
import select # uselect


wlanAccessPoint = network.WLAN( network.AP_IF ) # create access-point interface

wlanAccessPoint.config( essid = SSID, password = PASSWORD ) # ESP-8266 and ESP-32
# wlanAccessPoint.config( essid = SSID, password = PASSWORD, max_clients = MAX_CLIENTS ) # ESP32
    
wlanAccessPoint.active( True )  # activate the interface

print( wlanAccessPoint.ifconfig()[0] )

# A internet stream server-socket: this server-socket creates the clientSockets.
serverSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

# To prevent "OSError: [Errno 98] Address already in use",
# when a previous execution has left the socket in a TIME_WAIT state,
# and so can’t be immediately reused:

#   SOL_SOCKET:   Socket Options That Apply to the Socket Layer
#   SO_REUSEADDR: Indicates if the local socket address can be reused.
#                 This option is supported by sockets with an address family
#                 of AF_INET or AF_INET6 and a type of SOCK_STREAM or SOCK_DGRAM.
#   1:            A value of 0 (default) disables the option.
#                 A non-zero value sets the option indicating the local socket address can be reused.

serverSocket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

try:
    serverSocket.bind( ( '', 80 ) ) # everyone can connect
    serverSocket.listen( MAX_CLIENTS )
except Exception as _e:
    print( _e )


# Register serverSocket for polling (POLLIN: only poll for input)
poll = select.poll()
poll.register( serverSocket, select.POLLIN )


#######################################
# Extract request-path from header:
# For example:
#   In browser:      "http://192.168.4.1/led/On"
#   ==> strRequest:  "GET /led/On"
#   This function removes the "GET " and returns in this example "/led/On".

def getPathFromRequest( strRequest ) :
    iRequestPathStart = strRequest.find( "GET " ) # Every http request starts with "GET "

    if iRequestPathStart >= 0 :                    # followed by the request-path delimited with a ' ' charakter.
        iRequestPathStart += 4

        iRequestPathEnd = strRequest.find( " ", iRequestPathStart )

        if iRequestPathEnd >= 0 :
            return strRequest[ iRequestPathStart : iRequestPathEnd ]

    return ""
    

def sendHttpHeader( strResponseType, strContentType, clientSocket ):
    clientSocket.send( "HTTP/1.1 " )
    clientSocket.send( strResponseType )
    clientSocket.send( "\nContent-Type: text/" )
    clientSocket.send( strContentType )
    clientSocket.send( "; charset=UTF-8\n" ) # we send html and text is encoded in UTF-8
    clientSocket.send( "Connection: close\n\n" ) # We are (suspending and) closing the connection after sending the data.

def sendFile( strFileName, clientSocket ):    
    with open( strFileName, 'r' ) as f:
        while True:
            chunk = f.read(1024) # Read the next 1KB chunk
            
            if not chunk:
                break
                
            clientSocket.send(chunk) # Send the next 1KB chunk
            
            
#######################################
# Loop
# Listen for connecting clients and
# handle requests
import time
import display
display = display.Display()
display.setCenter( 64, 32 )

import re

PATTERN_JOYSTICK = re.compile( "/joystick/(.*)_(.*)" )

fSpeed  = 0
fGear   = 0

from motor import Motor

motorL = Motor( 12, 13,
    iFrequency     = 300,
    iDutyMinLeft   = 220,
    iDutyMaxLeft   = 1023,
    iDutyMinRight  = 220,
    iDutyMaxRight  = 1023,
    fSpeedMaxLeft  = -1.0,
    fSpeedMaxRight =  1.0 )

motorR = Motor( 18, 22,
    iFrequency     = 300,
    iDutyMinLeft   = 220,
    iDutyMaxLeft   = 1023,
    iDutyMinRight  = 220,
    iDutyMaxRight  = 1023,
    fSpeedMaxLeft  = -1.0,
    fSpeedMaxRight =  1.0 )

try:
    while True:
        aEvent = poll.poll( POLL_TIME_MILLIS ) # wait POLL_TIME_MILLIS, then give other tasks a chanche, to do there work.
        
        # check if we have stuff to handle
        
        if aEvent:
            # Only serverSocket is registered for polling, so only this one can be in the list (aEvent)
            
            try:
                # The return value is a pair (clientSocket, clientAddress)
                # where clientSocket is a new socket object where we can
                # receive data from and send data to:
                clientSocket, clientAddress = serverSocket.accept()

                strPath = getPathFromRequest( str( clientSocket.recv( 1024 ) ) ) # read maximal 1024 bytes
                
                # print( "Path: ", strPath )
                
                match = PATTERN_JOYSTICK.match( strPath )
            
                if match :
                    fGear  = float(match.group( 1 )) # x
                    fSpeed = float(match.group( 2 )) # y

                    # Here You have gear in[-1;1] and speed in [-1;1].
                    # Change this for Your needs.
                    #print( "Set: Gear = {}, speed = {}".format( fGear, fSpeed ) )
   
                    motorL.setSpeed( fSpeed + fGear )
                    motorR.setSpeed( fSpeed - fGear )
        
                  
                    sendHttpHeader( "200 OK", "plain", clientSocket )
                    clientSocket.send( match.group( 1 ) + ";" + match.group( 2 ) )
                   
                elif strPath == "/" :
                    sendHttpHeader( "200 OK", "html", clientSocket )
                    sendFile( "/index.html", clientSocket )
                             
                elif strPath == "/default.css" :
                    sendHttpHeader( "200 OK", "css", clientSocket )
                    sendFile( "/default.css", clientSocket )

                elif strPath == "/default.js" :
                    sendHttpHeader( "200 OK", "javascript", clientSocket )
                    sendFile( "/default.js", clientSocket )
                             
                else:
                    sendHttpHeader( "404 Not Found", "html", clientSocket )
                    sendFile( "/error404.html", clientSocket )

            except Exception as _e:
                print( _e )

            finally:
                try   : clientSocket.close()
                except: pass

        # Do something in the "background":
        display.clear()
        display.circle( 0,0,6)
        display.fillCircle( int(fGear*25), -int(fSpeed*25), 4 )
        display.show()
        
except KeyboardInterrupt:
    pass # User has typed "Ctrl C"

finally:
    # Clean up:
    try   : serverSocket.close()
    except: pass

    try   : wlanAccessPoint.active( False )  
    except: pass

    motorR.deinit()
    motorL.deinit()

    import gc
    gc.collect()