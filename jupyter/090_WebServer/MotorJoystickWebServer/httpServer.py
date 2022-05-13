MAX_REQUEST_LENGTH = 1024

#================================================

import network
import socket # usocket
import select # uselect

import info
import ubinascii
import re
import gc


#================================================

class ContentType :
    PLAIN      = "plain"
    HTML       = "html"
    CSS        = "css"
    JAVASCRIPT = "javascript"


#================================================

class RequestHandler :
    def __init__( self, strResponseType = "200 OK", strContentType = ContentType.HTML ) :
        self._strResponseType = strResponseType
        self._strContentType  = strContentType
        
    def dispatch( self, socketClient, strPath = None, match = None ) :
        pass
    
    def sendHeader( self, socketClient ) :
        socketClient.send( "HTTP/1.1 " )
        socketClient.send( self._strResponseType   )
        socketClient.send( "\nContent-type: text/" )
        socketClient.send( self._strContentType    )
        socketClient.send( "; charset=UTF-8\n"     )
        socketClient.send( "Connection: close\n\n" )

    def deinit():
        pass
    
    def __str__( self ) :
        return "Name: " + self.__class__.__name__ + " Response type: " + self._strResponseType + " Content type: " + self._strContentType
    
#================================================
    

class StringRequestHandler( RequestHandler ) :
    def __init__( self, strData, strResponseType = "200 OK", strContentType = ContentType.HTML ) :
        super().__init__( strResponseType, strContentType )
        self._strData = strData
        
    def dispatch( self, socketClient, strPath = None, match = None ) :
        self.sendHeader( socketClient )
        socketClient.sendall( self._strData )

        
class FileRequestHandler( RequestHandler ) :
    def __init__( self, strFileName, strResponseType = "200 OK", strContentType = ContentType.HTML ) :
        super().__init__( strResponseType, strContentType )
        self._strFileName    = strFileName
        
    def dispatch( self, socketClient, strPath = None, match = None ) :
        self.sendHeader( socketClient )
        
        with open(self._strFileName, 'r') as f:
            while True:
                chunk = f.read(1024) # Read the next 1KB chunk
                if not chunk:
                    break
                socketClient.send(chunk) # Send the next 1KB chunk

            #socketClient.sendall( f.read() )

class Error404RequestHandler( FileRequestHandler ) :
    def __init__( self, strFileName, strContentType = ContentType.HTML ) :
        super().__init__( strFileName, "404 Not Found", strContentType )
        

#================================================
  
class AccessPointHttpServer:
    def __init__( self, pollTimeMillis = 100 ) :
        self.ipAddress  = "?.?.?.?"
        self.subnetMask = self.ipAddress
        self.gateway    = self.ipAddress
        self.dnsServer  = self.ipAddress
        self.macAddress = "?:?:?:?:?:?"
        self.socketServer  = None
        
        self.pollTimeMillis = pollTimeMillis
        self.poll = select.poll()

        self.aPathRequestHandler    = []
        self.error404RequestHandler = Error404RequestHandler( "/error404.html" )
        
        
    def start( self, ssid = "ESP32 http server", password = "123123123123", maxClients = 5 ):
        self.wlanAccessPoint = network.WLAN( network.AP_IF ) # create access-point interface

        if info.TYPE == "Esp8266 Croduino Nova" :
            self.wlanAccessPoint.config( essid = ssid, password = password ) # Esp8266
        else :
            self.wlanAccessPoint.config( essid = ssid, password = password, max_clients = maxClients ) # ESP32

        self.wlanAccessPoint.active( True )                  # activate the interface

        # print( self.wlanAccessPoint.ifconfig()[0] )

        # A internet stream server-socket: this server-socket creates the clientSockets.
        self.socketServer = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        
        
        # To prevent "OSError: [Errno 98] Address already in use",
        # when a previous execution has left the socket in a TIME_WAIT state,
        # and so can’t be immediately reused:

        #   SOL_SOCKET:   Socket Options That Apply to the Socket Layer
        #   SO_REUSEADDR: Indicates if the local socket address can be reused.
        #                 This option is supported by sockets with an address family
        #                 of AF_INET or AF_INET6 and a type of SOCK_STREAM or SOCK_DGRAM.
        #   1:            A value of 0 (default) disables the option.
        #                 A non-zero value sets the option indicating the local socket address can be reused.

        self.socketServer.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        try:
            self.socketServer.bind( ( '', 80 ) ) # everyone can connect
            self.socketServer.listen( maxClients )

            # Register socketServer for polling (POLLIN: only poll for input)
            self.poll.register( self.socketServer, select.POLLIN )

            
            self.ipAddress, self.subnetMask, self.gateway, self.dnsServer = self.wlanAccessPoint.ifconfig() # [IP address, subnet mask, gateway, DNS server]
            self.macAddress = ubinascii.hexlify( network.WLAN().config('mac'),':' ).decode()
            
        except Exception as e:
            #print( "Exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args))
            print( e )

        gc.collect()

        
    def stop( self ):
        for pathRequestHandler in self.aPathRequestHandler :
            try: pathRequestHandler[1].deinit()
            except: pass
                
        try : self.socketServer.close()
        except: pass
    
        try : self.wlanAccessPoint.active( False ) 
        except: pass
    
        gc.collect()

    
    def dispatch( self, socketClient ) :
        bDispatched = False
        
        strPath = self.getRequestPath( str( socketClient.recv( MAX_REQUEST_LENGTH ) ) )

        for pathRequestHandler in self.aPathRequestHandler :
            match = pathRequestHandler[0].match( strPath ) # re.match( r'(/path/)(.*)', line)
            
            #print( "dispatch: " + strPath + " - " + str( match ) )
            
            if match :
                #print( "match: " +  strPath )
                pathRequestHandler[1].dispatch( socketClient, strPath, match )
                bDispatched = True
                break
            # else :
                # print( "not match: " + _strPath + " - "  + str( pathRequestHandler[1] ) )
                
        if bDispatched == False :
            self.error404RequestHandler.dispatch( _connection )
            

    def accept( self ):
        aEvent = self.poll.poll( self.pollTimeMillis ) # wait pollTimeMillis, then give other tasks a chanche, to do there work.
        
        # check if we have stuff to handle
        
        if aEvent:
            # Only socketServer is registered for polling, so only this one can be in the list (aEvent)
            
            socketClient = None
            
            try:
                # The return value is a pair (clientSocket, clientAddress)
                # where clientSocket is a new socket object where we can
                # receive data from and send data to:
                socketClient = self.socketServer.accept()[ 0 ]

                self.dispatch( socketClient )

            except Exception as _e:
                print( _e )
                #print( "Exception of type {0} occurred. Arguments:\n{1!r}".format(type(_e).__name__, _e.args))

            finally :
                #print(socketClient)
                try : socketClient.close()
                except: pass

        
    def getRequestPath( self, strRequest ) :
        # url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).decode("utf-8").rstrip("/")
        iRequestPathStart = strRequest.find( "GET " )

        if iRequestPathStart >= 0 :
            iRequestPathStart += 4
            
            iRequestPathEnd = strRequest.find( " ", iRequestPathStart )

            if iRequestPathEnd >= 0 :
                return strRequest[ iRequestPathStart : iRequestPathEnd ]
            
        return "/"
    
 
    def addRequestHandler( self, strPath, requestHandler ) :
        self.aPathRequestHandler.append( ( re.compile( strPath ), requestHandler ) )

    def __str__( self ) :
        return "Name: " + self.__class__.__name__ + ", IP address: " + self.ipAddress + ", Subnet mask: " + self.subnetMask + ", Gateway: " + self.gateway + ", DNS server: " + self.dnsServer + ", MAC address: " + self.macAddress
        