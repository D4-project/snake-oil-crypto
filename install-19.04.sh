#!/bin/bash
set -e
set -u
sudo apt-get install -y python3 redis-server postgresql postgresql-server-dev-all
sudo systemctl enable redis-server.service
sudo systemctl restart redis-server.service
wget http://www-ftp.lip6.fr/pub/math/sagemath/src/sage-8.9.tar.gz
md5sum -c sagesum.txt
if [$? = 1]; then
       	exit 1
fi
sudo apt-get install build-essential m4 dpkg-dev
tar -xvf sage-8.9.tar.gz
pushd sage-8.9
make configure
./configure --with-python=3
make build
sudo -ln -sr sage /usr/local/bin/sage 
sage -pip install redis rq psycopg2 factordb-pycli
