#!/bin/sh

DISTRIBTE_VER=0.6.49
./pyenv-3.3.py py3.3
source py3.3/bin/activate
curl -l -O "https://pypi.python.org/packages/source/d/distribute/distribute-${DISTRIBTE_VER}.tar.gz"
tar xf distribute-${DISTRIBTE_VER}.tar.gz
cd distribute-${DISTRIBTE_VER}
../py3.3/bin/python setup.py install
cd ..
./py3.3/bin/easy_install-3.3 pip


