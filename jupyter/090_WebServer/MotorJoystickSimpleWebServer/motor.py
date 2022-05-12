import machine

class Motor :
    def __init__( self, 
            iPinA, 
            iPinB,
            iFrequency     = 1000,
            iDutyMinLeft   =    0,  # Duty for speed = 0:              motor turns left
            iDutyMaxLeft   = 1023,  # Duty for speed = fSpeedMaxLeft:  motor turns left
            iDutyMinRight  =    0,  # Duty for speed = 0:              motor turns right
            iDutyMaxRight  = 1023,  # Duty for speed = fSpeedMaxRight: motor turns right
            fSpeedMaxLeft  = -1.0,  # Minimal value for setSpeed() --> iDutyMaxLeft
            fSpeedMaxRight =  1.0   # Maximal value for setSpeed() --> iDutyMaxRight
        ) :
        self._iFrequency    = iFrequency
        self._fScaleLeft    = (iDutyMaxLeft  - iDutyMinLeft )/fSpeedMaxLeft
        self._fScaleRight   = (iDutyMaxRight - iDutyMinRight)/fSpeedMaxRight
        self._iDutyMinLeft  = iDutyMinLeft
        self._iDutyMaxLeft  = iDutyMaxLeft
        self._iDutyMinRight = iDutyMinRight
        self._iDutyMaxRight = iDutyMaxRight
        
        self._fCurSpeed     = 0
        
        self._pwmA = machine.PWM( machine.Pin(iPinA, machine.Pin.OUT), freq=self._iFrequency, duty=0)
        self._pwmB = machine.PWM( machine.Pin(iPinB, machine.Pin.OUT), freq=self._iFrequency, duty=0)
        
        self._pwmDir   = self._pwmA
        self._pwmSpeed = self._pwmB
        
    def speedToDuty( self, fSpeed ) :
        if fSpeed == 0 :
            return 0
        elif fSpeed < 0 :
            return min( self._iDutyMaxLeft, max( self._iDutyMinLeft, int(self._iDutyMinLeft  + fSpeed*self._fScaleLeft +0.5) ) )
        else :
            return min( self._iDutyMaxRight, max( self._iDutyMinRight, int(self._iDutyMinRight + fSpeed*self._fScaleRight+0.5) ) )
            
    
    def setLeft( self ) :
        self._pwmDir   = self._pwmA
        self._pwmDir.duty( 0 )
        self._pwmSpeed = self._pwmB
      
    def setRight( self ) :
        self._pwmDir   = self._pwmB
        self._pwmDir.duty( 0 )
        self._pwmSpeed = self._pwmA
      
    def setSpeed( self, fSpeed ) :
        if fSpeed != self._fCurSpeed :
            iDuty = self.speedToDuty( fSpeed )
            
            if fSpeed > 0 and self._fCurSpeed <= 0 :
                self.setLeft()

            elif fSpeed < 0 and self._fCurSpeed >= 0 :
                self.setRight()
            
            self._pwmSpeed.duty( iDuty )
        
        self._fCurSpeed = fSpeed
        
    def deinit( self ):
        self.setSpeed( 0 )

        self._pwmSpeed.deinit()
        self._pwmDir.deinit()
