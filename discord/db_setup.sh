sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt add -
sudo apt-get update
sudo apt-get -y install postgresql

sudo -i -u postgres psql -c "CREATE USER akajukus WITH PASSWORD 'diocane96'; CREATE DATABASE discord;"

sudo -i -u postgres pg_dump discord > discord.sql