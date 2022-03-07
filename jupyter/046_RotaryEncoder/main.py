# Robust Rotary encoder reading
# Copyright John Main - best-microcontroller-projects.com
# Adapted to Python - Alfred Fuchs
# https://www.best-microcontroller-projects.com/rotary-encoder.html
# Improved Table Decode

class AverageFilter :
    def __init__(self,len):
        self.length   = len
        self.iLast    = len
        self.aData    = [0]*len # [i for i in range( len )]
        self.fAverage = 0
        self.isFull   = False
        
    def getAverage(self):
        return self.fAverage
        
    def add(self,val):
        self.iLast = (self.iLast - 1) % self.length
        self.fAverage += ((val - self.aData[self.iLast])/self.length)
        self.aData[self.iLast] = val

    def clear(self):
        for iIndex in range( self.length ) :
            self.aData[iIndex] = 0
        
        self.fAverage = 0
        
    def __str__(self) :
        return( "{}  {} ==> Average = {}".format( self.__class__, self.aData[self.iLast:] + self.aData[:self.iLast], self.fAverage ) )
    
    
from machine import Pin

class RotaryEncoder :
    _rot_enc_table = [0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0]
    
    def __init__( self, iPinCLK, iPinDT, iLeftBound = None, iRightBound = None, bCycle = False, bNoisyEncoder = True, scale = 1 ) :
        self._bNoisyEncoder = bNoisyEncoder
        self._pinCLK        = Pin( iPinCLK, Pin.IN, Pin.PULL_UP )
        self._pinDT         = Pin( iPinDT,  Pin.IN, Pin.PULL_UP )
        self._prevNextCode  = 0
        self._store         = 0
        self._value         = 0
        self._iLeftBound    = iLeftBound
        self._iRightBound   = iRightBound
        self._bCycle        = bCycle
        self._scale         = scale
        self._diffMillis    = 0
        self._lastMillis    = 0
        self._averageFilter = AverageFilter( 5 )

    # A valid CW or CCW move returns 1, invalid returns 0.
    def read_rotary( self ) :
        self._prevNextCode <<= 2

        if self._pinDT .value() == 0 : self._prevNextCode |= 0x02
        if self._pinCLK.value() == 0 : self._prevNextCode |= 0x01

        self._prevNextCode &= 0x0f


        # If valid then store as 16 bit data.
        if RotaryEncoder._rot_enc_table[self._prevNextCode] != 0 :
            self._store = int( self._store << 4 )
            self._store |= self._prevNextCode
            self._store &= 0xffff
            
            if self._bNoisyEncoder == True :
                if (self._store & 0xff) == 0x2b: return -1
                if (self._store & 0xff) == 0x17: return 1
            else :
                if self._store == 0xd42b : return  1
                if self._store == 0xe817 : return -1

        return 0;

    def update( self ) :
        step = self.read_rotary()

        if step != 0:
            self._diffMillis = time.ticks_diff(time.ticks_ms(), self._lastMillis)
            self._lastMillis += self._diffMillis
            
            if self._diffMillis > 190:
                self._averageFilter.clear()
                
            self._averageFilter.add( max(0, (190 - self._diffMillis)/20) )
            #print( self._diffMillis, self._averageFilter )

            self._value += (step*(1<<round(self._averageFilter.getAverage())) )
            #print( step*(1<<round(self._averageFilter.getAverage())) )
            #self._value += (step*max(1, 190 - self._diffMillis))
            
            if step == 1 :
                if self._iRightBound is not None and self._value > self._iRightBound :
                    self._value = self._iLeftBound if self._bCycle else self._iRightBound

            elif step == -1 :
                if self._iLeftBound is not None and self._value < self._iLeftBound :
                    self._value = self._iRightBound if self._bCycle else self._iLeftBound
            
            return True
        
        else :
            return False
        
    def value( self ) :
        return self._value
    
    def __str__(self) :
        strDirection = "<--" if self._prevNextCode == 0x0b else "-->" if self._prevNextCode == 0x07 else "???"

        return ( strDirection + " value = " + str( self._value ) + ", store = " + hex(self._store) + ", prevNextCode = " + hex( self._prevNextCode ) )



# Sample
from machine import Pin, Timer

led = Pin(13, Pin.OUT) # 25 HelTec, 13 Croduino
led.off()

rotaryEncoder = RotaryEncoder( 2, 22, iLeftBound = 0, iRightBound = 1000 )

from display import Display

display = Display()

timerLEDOn  = Timer(1)
timerLEDOff = Timer(2)

iPeriod = 100

# Is called when timer-intetrupt occures:
def ledTimerOnInterruptHandler(timer):
    led.on()
    timerLEDOff.init(period=1, mode=Timer.ONE_SHOT, callback=ledTimerOffInterruptHandler)
        
def ledTimerOffInterruptHandler(timer):
    led.off()
    timerLEDOn.init(period=iPeriod, mode=Timer.ONE_SHOT, callback=ledTimerOnInterruptHandler)
    


try:
    ledTimerOnInterruptHandler( None )
    
    while True:
        if rotaryEncoder.update() == True:
            iPeriod = rotaryEncoder.value()
            display.fill_rect( 0, 0, 127, 10, 0 )
            display.text( str(iPeriod), 0, 0 )
            display.show()

except KeyboardInterrupt:
    pass
finally:    
    timerLEDOn.deinit()
    timerLEDOff.deinit()
    led.off()
    display.text( "Done.", 0, 50 )
    display.show()
    print( "DONE." )
    