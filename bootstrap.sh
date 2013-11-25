#!/usr/bin/env bash 
apt-get update -y
apt-get install -y sudo
apt-get install -y python-setuptools build-essential python-pip  
ln -fs /vagrant /opt/cc
pip install virtualenv virtualenvwrapper
echo "export WORKON_HOME=\$HOME/.virtualenvs" >> /etc/skel/.bashrc
echo "export PROJECT_HOME=/opt/cc" >> /etc/skel/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> /etc/skel/.bashrc


 
