@ECHO OFF


ECHO ##########################################
ECHO Start jupyter lab in folder %__CD__%
ECHO ##########################################
ECHO.

ECHO. & ECHO ##########################################
ECHO Activate virtual environment

call .\env\Scripts\activate

ECHO. & ECHO ##########################################
ECHO Update "jupyter_micropython_kernel"
python -m jupyter_micropython_kernel.install

ECHO. & ECHO ##########################################
ECHO Start jupyter-lab with notebook-dir "%OneDrive%\WPFInformatik\jupyter"
jupyter-lab --notebook-dir "%OneDrive%\WPFInformatik\jupyter"

ECHO. & ECHO ##########################################
ECHO Done.
ECHO ##########################################

pause

