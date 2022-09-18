sudo apt-get update -y
sudo apt-get groupinstall "Development Tools" -y
sudo apt-get install openssl11 openssl11-devel  libffi-devel bzip2-devel wget -y

wget https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tgz
tar -xf Python-3.10.4.tgz
cd Python-3.10.4/
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall

cd
sudo apt-get install python3-pip locate
sudo apt-get install postgresql libpq-dev postgresql-client postgresql-client-common
mkdir ~/discord && cd ~/discord
python3.10 -m venv discord_venv
source discord_venv/bin/activate


python -m pip install -r requirements.txt
