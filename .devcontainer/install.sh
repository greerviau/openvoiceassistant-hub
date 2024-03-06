CWD=$(pwd)
echo $CWD

python3.11 -m venv env

source env/bin/activate

python -m pip install --upgrade pip
python -m pip install --upgrade wheel