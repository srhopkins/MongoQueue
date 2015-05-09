#!/usr/bin/env bash

#sed -i "s/<password>/${PASSWORD}/" /root/.pypirc

python setup.py register -r ${ENV}

python setup.py sdist upload -r ${ENV}

python setup.py bdist_wheel upload -r ${ENV}
