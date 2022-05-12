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
    
    constructor()
    {
        let htmlSliderSpeed       = document.getElementById( "idSliderSpeed" );
        let htmlOutputSliderSpeed = document.getElementById( "idSliderSpeedOutput" );

        let htmlButtonStop        = document.getElementById( "idButtonStop" );

        let bIsWaitingSpeed       = false; // only to avoid "overload"

        // htmlOutputSliderSpeed.innerHTML = htmlSliderSpeed.value;
        
        let iSliderMaxAbs = Math.max( Math.abs(htmlSliderSpeed.min), Math.abs(htmlSliderSpeed.max) );
        
        htmlButtonStop.addEventListener(
            "click",
            function() {
                htmlSliderSpeed.value = 0;
                htmlSliderSpeed.dispatchEvent(new Event('input', { bubbles: true }));
            }
        )

        let dataSender = new AjaxDataSender(); // ConsoleDataSender();
        
        htmlSliderSpeed.addEventListener(
            "input",
            function( _event ) {
                dataSender.send( "/speed/" + RemoteControllApp.roundn( _event.target.value/iSliderMaxAbs ) ); //, strResult => console.log( strResult ) );
            }
        )
    }
    
    
}

