#!/usr/bin/env bash 
apt-get update -y
apt-get install -y sudo build-essential libjpeg-dev python-dev git-core 
apt-get install -y postgresql libpq-dev memcached redis-server imagemagick
apt-get install -y python-setuptools  python-pip
apt-get install -y tomcat6 tomcat6-admin tomcat6-common 
apt-get install -y libjpeg-dev libfreetype6-dev libgif-dev swftools mupdf
ln -fs /vagrant /opt/cc
pip install virtualenv virtualenvwrapper python-memcached
echo "export WORKON_HOME=\$HOME/.virtualenvs" >> /etc/skel/.bashrc
echo "export PROJECT_HOME=/opt/cc" >> /etc/skel/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> /etc/skel/.bashrc

echo "export WORKON_HOME=\$HOME/.virtualenvs" >> /home/vagrant/.bashrc
echo "export PROJECT_HOME=/opt/cc" >> /home/vagrant/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> /home/vagrant/.bashrc
 
