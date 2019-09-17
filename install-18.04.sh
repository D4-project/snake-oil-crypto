#!/bin/bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get install -y python3.7 python3.7-venv redis-server
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
python3.7 -m venv VENV
. ./VENV/bin/activate
make configure
./configure --with-python=3
make -j4 build
sudo ln -sr sage /usr/local/bin/sage
deactivate
rm -rf VENV
sage -i ipython
sage -pip install -r requirements.txt
