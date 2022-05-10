document.addEventListener(
    'DOMContentLoaded',
    function() { new RemoteControllApp(); },
    false
);
  
class RemoteControllApp
{
    static ROUND_N = 3;
    
    constructor()
    {
        this.strLastUrl = undefined
        
        let htmlSliderSpeed       = document.getElementById( "idSliderSpeed" );
        let htmlOutputSliderSpeed = document.getElementById( "idSliderSpeedOutput" );

        let htmlButtonStop        = document.getElementById( "idButtonStop" );

        let bIsWaitingSpeed       = false; // only to avoid "overload"

        htmlOutputSliderSpeed.innerHTML     = htmlSliderSpeed.value;


        htmlButtonStop.addEventListener(
            "click",
            function() {
                htmlSliderSpeed.value = 0;
                htmlSliderSpeed.dispatchEvent(new Event('input', { bubbles: true }));
            }
        )

        let objThis = this
        
        htmlSliderSpeed.addEventListener(
            "input",
            function( _event ) {
                objThis.sendAjaxRequest( "/speed/" + _event.target.value, strResult => console.log( strResult ) );
            }
        )
    }
    
    
    roundn( _num, _n = JoystickApp.ROUND_N )
    {
        return parseFloat((Math.round(_num * 10**_n) / 10**_n).toFixed(_n));
    }
    
    
    sendAjaxRequest( _url, _responseHandler = undefined )
    {
        let objThis = this;
        
        if ( this.isWaiting )
        {
            objThis.strLastUrl = _url
            return
        }
        
        this.isWaiting = true;
                
        objThis.strLastUrl = undefined
        
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
                    if ( _responseHandler !== undefined )
                    {
                        _responseHandler( xhttp.responseText );
                    }
                    
                    console.log( "Status " + status  + " Response text " + xhttp.responseText )
                }
                else
                {
                    // Error
                }
                
                objThis.isWaiting = false;
                
                if ( objThis.strLastUrl != undefined )
                {
                    objThis.sendAjaxRequest( objThis.strLastUrl ) 
                }

            }
        };
        
        // console.log( "Send: " + _url )
        xhttp.send();
    }    
}

