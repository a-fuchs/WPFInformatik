@ECHO OFF

set JUPYTER_BASE_FOLDER=%__CD__%
REM set JUPYTER_DRIVE="P"
set JUPYTER_FOLDER=jupyter

ECHO ##########################################
ECHO Install jupyter lab
ECHO ##########################################
ECHO.

REM %JUPYTER_DRIVE%
REM cd \

if not exist "%JUPYTER_FOLDER%" (
    REM ECHO Creating folder %JUPYTER_DRIVE%\%JUPYTER_FOLDER%
    ECHO Creating folder %JUPYTER_BASE_FOLDER%%JUPYTER_FOLDER%
    mkdir "%JUPYTER_FOLDER%"
)


REM :INSTALL_JUPYTER

cd "%JUPYTER_FOLDER%"

ECHO Set current folder  %__CD__%


ECHO. & ECHO ##########################################
ECHO Create virtual environmend: %__CD__%env
python -m venv env


ECHO Activate virtual environment
call .\env\Scripts\activate


ECHO. & ECHO ##########################################
ECHO upgrade pip
python -m pip --timeout 100 install --upgrade pip

ECHO. & ECHO ##########################################
ECHO install: jupyterlab
python -m pip  --timeout 100 install jupyterlab

ECHO. & ECHO ==========================================
ECHO install: jupyter_micropython_kernel
python -m pip  --timeout 100 install jupyter_micropython_kernel

ECHO. & ECHO ==========================================
ECHO install: pandas
python -m pip  --timeout 100 install pandas

ECHO. & ECHO ==========================================
@ECHO install: numpy
python -m pip  --timeout 100 install numpy

ECHO. & ECHO ==========================================
ECHO install: plotly
python -m pip  --timeout 100 install plotly

ECHO. & ECHO ==========================================
ECHO install: matplotlib
python -m pip  --timeout 100 install matplotlib

ECHO. & ECHO ==========================================
ECHO install: kaleido"
python -m pip  --timeout 100 install kaleido

ECHO. & ECHO ==========================================
ECHO install: scipy
python -m pip  --timeout 100 install scipy


ECHO. & ECHO ==========================================
REM ECHO setup: jupyter_micropython_kernel
REM python -m jupyter_micropython_kernel.install

ECHO. & ECHO ##########################################
ECHO Done.
ECHO ##########################################

pause
