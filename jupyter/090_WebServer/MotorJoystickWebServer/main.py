from httpServer import RequestHandler, FileRequestHandler, ContentType, AccessPointHttpServer
from motor import Motor

#######################################
# class SpeedRequestHandler


gfGear  = 0
gfSpeed = 0


class SpeedRequestHandler( RequestHandler ) :
    def __init__( self ) :
        super().__init__( strContentType = ContentType.PLAIN )
        
        self._fSpeedCur = 0
        self._fGearCur  = 0
        
        self._motorL = Motor( 12, 13,
            iFrequency     = 300,
            iDutyMinLeft   = 220,
            iDutyMaxLeft   = 1023,
            iDutyMinRight  = 220,
            iDutyMaxRight  = 1023,
            fSpeedMaxLeft  = -1.0,
            fSpeedMaxRight =  1.0 )

        self._motorR = Motor( 18, 22,
            iFrequency     = 300,
            iDutyMinLeft   = 220,
            iDutyMaxLeft   = 1023,
            iDutyMinRight  = 220,
            iDutyMaxRight  = 1023,
            fSpeedMaxLeft  = -1.0,
            fSpeedMaxRight =  1.0 )
        
        
    def dispatch( self, socketClient, strPath = None, match = None ) :
        # Here You have velocity in[-1;1] and gear in [-1;1]
        global gfGear
        global gfSpeed
        
        gfGear  = float(match.group( 1 )) # x
        gfSpeed = float(match.group( 2 )) # y
        
        if gfSpeed != self._fSpeedCur or gfGear != self._fGearCur :
            self._motorL.setSpeed( gfSpeed + gfGear )
            self._motorR.setSpeed( gfSpeed - gfGear )
            
            self._fSpeed   = gfSpeed
            self._fGearCur = gfGear
            
            # print( "Set: Velocity = {}, Gear = {}".format( gfSpeed, gfGear ), end="" )
        
        self.sendHeader( socketClient )
        socketClient.send( match.group( 1 ) + ";" + match.group( 2 ) )

    def deinit():
        self._motorL.deinit()
        self._motorR.deinit()
        
#######################################
# Add Requesthandler to server
        
httpServer = AccessPointHttpServer()

httpServer.addRequestHandler( "/joystick/(.*)_(.*)", SpeedRequestHandler() )
httpServer.addRequestHandler( "/default.css", FileRequestHandler( "/default.css", strContentType = ContentType.CSS        ) )
httpServer.addRequestHandler( "/default.js",  FileRequestHandler( "/default.js",  strContentType = ContentType.JAVASCRIPT ) )
httpServer.addRequestHandler( "/",            FileRequestHandler( "/index.html" ) )


# and start server:
httpServer.start( ssid = "ESP32 MotorJoystick WebServer", password = "123123123123" )

print( httpServer )


#######################################
# Setup display:
import display

display = display.Display()

display.clear()
display.text( httpServer.ipAddress, 0, 10 )
display.show()
display.setCenter( 64, 32 )


#######################################
# disable the brownout-detector
def disableBrownOutDetector():
    from machine import mem32
    from micropython import const

    DR_REG_RTCCNTL_BASE    = const(0x3ff48000)
    RTC_CNTL_BROWN_OUT_REG = const(DR_REG_RTCCNTL_BASE + 0xd4)
    mem32[RTC_CNTL_BROWN_OUT_REG] = 0

# disableBrownOutDetector()


#######################################
# Loop

try :
    while True:
        # print( "\nWaiting for client..." ) # , end="" )
        httpServer.accept()
        
        # Do something useful in the "background":
        display.clear()
        display.circle( 0,0,6)
        display.fillCircle( int(gfGear*25), -int(gfSpeed*25), 4 )
        display.show()
        
except KeyboardInterrupt:
    pass # User has typed "Ctrl C"

finally:
    httpServer.stop()
    print( "\nServer stopped." )
    
    display.clear()
    display.setCenter( 0, 0 )
    display.text( "Server stopped.", 0, 30 )
    display.show()
    
    import gc
    gc.collect()    