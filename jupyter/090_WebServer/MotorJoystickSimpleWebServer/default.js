document.addEventListener(
    'DOMContentLoaded',
    function() { new RemoteControllApp(); },
    false
);


class DataSender
{
    constructor()
    {
        this.isWaiting  = false;
        this.strLastUrl = undefined;
    }
    
    send( _url )
    {
        if ( this.isWaiting )
        {
            this.strLastUrl = _url;
        }
        else
        {
            this.isWaiting  = true;
            this.strLastUrl = undefined;

            this.doSend( _url );
        }
    }    

    doSend( _url )
    {
        this.isWaiting = false;
    }
}


class ConsoleDataSender extends DataSender
{
    constructor()
    {
        super();
    }
    
    doSend( _url )
    {
        console.log( "Sending: " + _url );
        
        this.isWaiting = false;
    }
}


class AjaxDataSender extends DataSender
{
    constructor()
    {
        super();
    }
    
    doSend( _url )
    {
        let objThis = this;
        let xhttp   = new XMLHttpRequest();
        
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
                    console.log( "Status " + status  + " Response text " + xhttp.responseText );
                }
                else
                {
                    // Error
                }
                
                objThis.isWaiting = false;
                
                if ( objThis.strLastUrl != undefined )
                {
                    console.log( "==> Sending pending url: " + objThis.strLastUrl );
                    objThis.send( objThis.strLastUrl );
                }

            }
        };
        
        console.log( "Send: " + _url );
        
        xhttp.send();
    }    
}



class RemoteControllApp
{
    static ROUND_N = 3;
    
    static roundn( _num, _n = RemoteControllApp.ROUND_N )
    {
        return parseFloat((Math.round(_num * 10**_n) / 10**_n).toFixed(_n));
    }
    
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

        this.posXLast = 0;
        this.posYLast = 0;
        
        this.dataSender = new AjaxDataSender();
        // this.dataSender = new ConsoleDataSender();
        

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
            
            this.dataSender.send( "/joystick/" + RemoteControllApp.roundn( Math.min( 1.0, Math.max( -1.0, this.posX/this.radiusMax ) ) ) + "_" + (-RemoteControllApp.roundn( Math.min( 1.0, Math.max( -1.0, this.posY/this.radiusMax ) ) ) ) )
        }
    }
}