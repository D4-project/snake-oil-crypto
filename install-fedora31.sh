#!/bin/bash
set -e
set -u
sudo dnf install -y python3 redis postgresql libpq-devel wget
sudo systemctl enable redis.service
sudo systemctl restart redis.service
wget http://www-ftp.lip6.fr/pub/math/sagemath/src/sage-8.9.tar.gz
md5sum -c sagesum8.9.txt
if [$? = 1]; then
    exit 1
fi
sudo dnf -y install binutils xz gcc gcc-c++ gcc-gfortran make m4 perl tar git patch perl-ExtUtils-MakeMaker openssl openssl-devel zlib-devel bzip2 bzip2-devel xz-devel gmp gmp-devel libcurl-devel curl yasm pkg-config ntl-devel mpfr-devel libmpc-devel eclib-devel gmp-ecm-devel lrcalc-devel isl-devel givaro-devel pari-devel pari-elldata pari-seadata pari-galdata pari-galpol m4ri-devel m4rie-devel L-function-devel
tar -xvf sage-8.9.tar.gz
pushd sage-8.9
make configure
./configure --with-python=3
make -j4  build
sudo ln -sr sage /usr/local/bin/sage 
sage -pip install redis cryptography rq psycopg2 factordb-pycli sqlalchemy git+git://github.com/MISP/PyMISP
