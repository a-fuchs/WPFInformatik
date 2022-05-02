import machine
import time, math # for pulse()

class LED :
    def __init__( self, _pinNr, _isOn = False ) :
        self._pinNr = _pinNr
        self._pin = machine.Pin( self._pinNr, machine.Pin.OUT )
        self.set( _isOn )
        
    def on( self ):
        #self._pin = machine.Pin( self._pinNr, machine.Pin.OUT )
        self._pin.on()
        self._isOn = True
        
    def off( self ):
        #self._pin = machine.Pin( self._pinNr, machine.Pin.OUT )
        self._pin.off()
        self._isOn = False

    def set( self, _isOn ):
        #self._pin = machine.Pin( self._pinNr, machine.Pin.OUT )
        self._isOn = _isOn
        self._pin.on() if self._isOn else self._pin.off()
    
    def toggle( self ):
        self.set( not self._isOn )
        
    def isOn( self ):
        return self._isOn == True

    def isOff( self ):
        return self._isOn == False
    
    # this methode os blocking
    def pulse( self, _iCycles, _tSleepMillis ):
        pinPWM = machine.PWM( machine.Pin(self._pinNr), freq=1000) 
        
        for iCount in range( _iCycles ):
            for iIndex in range(20):
                pinPWM.duty(int(math.sin(iIndex / 10 * math.pi) * 500 + 500))
                time.sleep_ms(_tSleepMillis)
        
        pinPWM.deinit()

        
I_REPEAT = 5

def testLED( *_aPinId ):
    import time
    
    aLed = []
    
    for iIndex, pinId in enumerate( _aPinId ):
        aLed.append( LED( pinId ) )
    
    for led in aLed:
        led.off()
    
    print( "Blink all LEDs at same time" ) 
    for iMock in range(I_REPEAT):
        for led in aLed:
            led.toggle()
        time.sleep_ms(500)

    print( "Pules LEDs" )
    for led in aLed:
        #print( "["+str(iCount+1)+"/10]", end =", " )
        led.pulse(I_REPEAT, 50)
        
    print( "Blink all LEDS one after the other" )
    for iMock in range(I_REPEAT):
        for led in aLed:
            led.toggle()
            time.sleep_ms(100)

            
testLED( 2, 15, 16 )
        
print( "Done" )