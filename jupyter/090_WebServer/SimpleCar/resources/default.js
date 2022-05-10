document.addEventListener(
    'DOMContentLoaded',
    function() { new JoystickApp(); },
    false
);


class JoystickApp
{
    static ROUND_N = 3;
    
    constructor()
    {
        let objThis = this;

        this.isActive = false;
        this.posX   = 0;
        this.posY   = 0;
        this.startX = 0;
        this.startY = 0;

        this.htmlMainContainer  = document;
        this.htmlStickContainer = document.getElementById( "idStickContainer" );
        this.htmlStick          = document.getElementById( "idStick");

        this.radiusMax = this.htmlStickContainer.clientWidth/2 - 40;

        this.htmlMainContainer.addEventListener("touchstart", this.dragStart.bind(this), false);
        this.htmlMainContainer.addEventListener("touchend",   this.dragEnd.bind(this), false);
        this.htmlMainContainer.addEventListener("touchmove",  this.drag.bind(this), false);

        this.htmlMainContainer.addEventListener("mousedown",  this.dragStart.bind(this), false);
        this.htmlMainContainer.addEventListener("mouseup",    this.dragEnd.bind(this), false);
        this.htmlMainContainer.addEventListener("mousemove",  this.drag.bind(this), false);

        this.isWaiting = false; // only to avoid "overload"
        this.posXLast = 0;
        this.posYLast = 0;
        

        this.htmlButtonStop = document.getElementById( "idButtonStop" );

        this.htmlButtonStop.addEventListener(
            "click",
            function() {
                objThis.setTranslate(objThis.startX,objThis.startY);
            }
        )
        
    }

    dragStart( e )
    {
        if (e.target === this.htmlStick)
        {
            let ePointer = (e.type === "touchstart") ? e.touches[0] : e;

            this.startX = ePointer.clientX - this.posX;
            this.startY = ePointer.clientY - this.posY;

            this.isActive = true;
        }
    }

    drag(e)
    {
        if (this.isActive)
        {
            e.preventDefault();

            let ePointer = (e.type === "touchmove") ? e.touches[0] : e;

            this.setTranslate( ePointer.clientX, ePointer.clientY );
        }
    }

    dragEnd(e)
    {
        this.initialX = this.currentX;
        this.initialY = this.currentY;

        this.isActive = false;
    }

    sendAjaxRequest( _url )
    {
        if ( this.isWaiting )
        {
            return
        }
        
        this.isWaiting = true;
                
        let objThis = this;
        
        var xhttp = new XMLHttpRequest();
        
        xhttp.open( "GET", _url, true );
        
        xhttp.timeout = 2000; // time in milliseconds
                              // In Internet Explorer, the timeout property may be set only after calling the open() method and before calling the send() method.
        
        xhttp.ontimeout = function ( _e ) {
            objThis.isWaiting = false;
        };
            

        // xhr.onload = function () { // Request finished. Do processing here. };

        xhttp.onreadystatechange = function () {
            // In local files, status is 0 upon success in Mozilla Firefox
            
            if ( xhttp.readyState === XMLHttpRequest.DONE ) // this.readyState == 4
            {
                let status = xhttp.status;

                if ( status === 0 || (status >= 200 && status < 400) )
                {
                    // The request has been completed successfully
                    document.getElementById("idOutput").innerHTML = xhttp.responseText;
                    // console.log( "Status " + status  + " Response text " + xhttp.responseText )
                }
                else
                {
                    // Error
                }
                
                objThis.isWaiting = false;
            }
        };
        
        console.log( "Send: " + _url )
        xhttp.send();
    }
    
    
    roundn( _num, _n = JoystickApp.ROUND_N )
    {
        return parseFloat((Math.round(_num * 10**_n) / 10**_n).toFixed(_n));
    }
    
    setTranslate( clientX, clientY )
    {
        this.posX = clientX - this.startX;
        this.posY = clientY - this.startY;

        let radiusPos = Math.sqrt( this.posX**2 + this.posY**2 );

        if ( radiusPos > this.radiusMax )
        {
            this.posX *= this.radiusMax/radiusPos
            this.posY *= this.radiusMax/radiusPos
        }
        
        this.posX = Math.round( this.posX )
        this.posY = Math.round( this.posY )
        
        if ( this.posX != this.posXLast || this.posY != this.posYLast )
        {
            this.posXLast = this.posX
            this.posYLast = this.posY

            this.htmlStick.style.transform = "translate3d(" + this.posX + "px, " + this.posY + "px, 0)";

            this.sendAjaxRequest( "/joystick/" + this.roundn( Math.min( 1.0, Math.max( -1.0, this.posX/this.radiusMax ) ) ) + "_" + (-this.roundn( Math.min( 1.0, Math.max( -1.0, this.posY/this.radiusMax ) ) ) ) )
        }
        

    }
}

