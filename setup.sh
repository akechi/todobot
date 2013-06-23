#!/bin/sh

./pyenv-3.3.py py3.3
source py3.3/bin/activate
curl -O "http://pypi.python.org/packages/source/d/distribute/distribute-0.6.28.tar.gz"
tar xf distribute-0.6.28.tar.gz
cd distribute-0.6.28
python setup.py install
cd ..
./py3.3/bin/easy_install-3.3 pip


