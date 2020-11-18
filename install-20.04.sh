#!/bin/bash
set -e
set -u
sudo apt-get install -y python3 redis-server postgresql postgresql-server-dev-all
sudo ln -s /usr/bin/python3 /usr/bin/python
sudo systemctl enable redis-server.service
sudo systemctl restart redis-server.service
wget http://www-ftp.lip6.fr/pub/math/sagemath/linux/64bit/sage-9.2-Ubuntu_20.04-x86_64.tar.bz2
md5sum -c sagesum9.2.txt
if [$? = 1]; then
       	#exit 1
fi
tar -xvf sage-9.2-Ubuntu_20.04-x86_64.tar.bz2
sudo ln -sr SageMath/sage /usr/local/bin/sage 
sage -pip install redis cryptography rq psycopg2 factordb-pycli SQLAlchemy git+git://github.com/MISP/PyMISP
