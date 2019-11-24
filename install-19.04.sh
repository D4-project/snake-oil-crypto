#!/bin/bash
sudo apt-get install -y python3 redis-server
sudo systemctl enable redis-server.service
sudo systemctl restart redis-server.service
wget http://www-ftp.lip6.fr/pub/math/sagemath/src/sage-8.8.tar.gz
md5sum -c sagesum.txt
if [$? = 1]; then
       	exit 1
fi
sudo apt-get install build-essential m4 dpkg-dev
tar -xvf sage-8.8.tar.gz
pushd sage-8.8
make configure
./configure --with-python=3
make -j8 build
sage -pip install redis rq psycopg2 factordb-pycli sqlachemy git+git://github.com/MISP/PyMISP
