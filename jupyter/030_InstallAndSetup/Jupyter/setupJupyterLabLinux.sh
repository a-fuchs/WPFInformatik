python -m venv env
source .\env\bin\activate

python -m pip  --timeout 100 install --upgrade pip
python -m pip  --timeout 100 install pandas
python -m pip  --timeout 100 install numpy
python -m pip  --timeout 100 install ipympl
python -m pip  --timeout 100 install plotly
python -m pip  --timeout 100 install matplotlib
python -m pip  --timeout 100 install kaleido
python -m pip  --timeout 100 install scipy
python -m pip  --timeout 100 install jupyterlab
python -m pip  --timeout 100 install jupyter_micropython_kernel
python -m jupyter_micropython_kernel.install
