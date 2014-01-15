Chinchilla Frontend
===================

How to run
----------

1. Clone the repo
2. Make new virtualenv and activate it
3. cd cc
4. pip install -r requirement.txt
5. cp cc/local_settings.py.sample cc/local_settings.py
6. Change the settings to match configuration in the local environment
7. python manage.py syncdb
8. python manage.py migrate
9. Start redis server: redis-server &
10. Start celeryd for converting files: python manage.py celeryd
11. Start django dev server in a different terminal: python manage.py runserver_plus

* Or use vagrant.
1. install vagrant and virtualbox
2. vagrant box add debain-wheezy  https://dl.dropboxusercontent.com/u/197673519/debian-7.2.0.box
3. edit the Vagrante file IP to meet your needs
4. edit bootstrap.sh, set your /vagrant to your workign dir. 
5. vagrant up  
6. vagrant ssh 
7. mkvirtualenv cc-app --no-site-packages --distribute 
8. workon cc-app


Other dependancies
------------------

- Python 2.7+
- PostgreSQL 9.0+
- Redis 2.4+
- lesscss
- pdf2json
- mupdf 1.3+ (dependancies in Ubuntu / Debian): libxtst-dev libx11-dev pkg-config
- flexpaper

Tips: in OSX use homebrew: `brew install redis imagemagick ghostscript`


How to deploy
-------------
cd cc/
fab deploy -R staging
