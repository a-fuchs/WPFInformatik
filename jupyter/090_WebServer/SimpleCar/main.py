from httpServer import RequestHandler, FileRequestHandler, ContentType, SimpleAccessPointHttpServer
from motor import Motor

class SpeedRequestHandler( RequestHandler ) :
    def __init__( self ) :
        super().__init__( strContentType = ContentType.PLAIN )
        self._fCurV    = 0
        self._fCurGear = 0
        self._motorL = Motor( 12, 13,
            iFrequency     = 100,
            iDutyMinLeft   = 330,
            iDutyMaxLeft   = 1023,
            iDutyMinRight  = 330,
            iDutyMaxRight  = 1023,
            fSpeedMaxLeft  = -1.0,
            fSpeedMaxRight =  1.0 )

        self._motorR = Motor( 18, 22,
            iFrequency     = 100,
            iDutyMinLeft   = 330,
            iDutyMaxLeft   = 1023,
            iDutyMinRight  = 330,
            iDutyMaxRight  = 1023,
            fSpeedMaxLeft  = -1.0,
            fSpeedMaxRight =  1.0 )
        
        
    def dispatch( self, socketClient, strPath = None, match = None ) :
        # Here You have velocity in[-1;1] and gear in [-1;1]
        
        fV    = float(match.group( 1 ))
        fGear = float(match.group( 2 ))
        
        if fV != self._fCurV or fGear != self._fCurGear :
            self._motorL.setSpeed( fV + fGear )
            self._motorR.setSpeed( fV - fGear )
            
            self._fCurV    = fV
            self._fCurGear = fGear
            
            #print( "Set: Velocity = {}, Gear = {}".format( fV, fGear ) )
            
            return True
        
        

# httpServer = httpServer.SimpleAccessPointHttpServer()
httpServer = SimpleAccessPointHttpServer()


httpServer.addRequestHandler( "/joystick/(.*)_(.*)", SpeedRequestHandler() )
httpServer.addRequestHandler( "/default.css", FileRequestHandler( "/resources/default.css", strContentType = ContentType.CSS        ) )
httpServer.addRequestHandler( "/default.js",  FileRequestHandler( "/resources/default.js",  strContentType = ContentType.JAVASCRIPT ) )
httpServer.addRequestHandler( "/",            FileRequestHandler( "/resources/index.html" ) )


httpServer.start( ssid = "ESP32 Simple car", password = "123123123123" )

print( httpServer )


#######################################
# Loop

try :
    while True:
        print( "Waiting for client...", end="" )
        httpServer.accept()
        
except KeyboardInterrupt:
    httpServer.stop()
    print( "Server stopped." )