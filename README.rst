Chinchilla Frontend
===================

How to run
----------

1. Clone the repo
2. Make new virtualenv and activate it*
3. cd cc
4. pip install -r requirement
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
- PostgreSQL 9.0+ (or MySQL/SQlite for development)
- Redis 2.4+
- ImageMagick 6.6+ (http://www.imagemagick.org/). On OS X it can be installed from MacPorts or Homebrew (if you are using Homebrew, Ghostscript has to be install separately). has to be installed with GhostScript, jpeg and png support. Png support can be turned on by passing path to X11 libs during ImageMagick configuration. Jpeg and Ghostscript have to be installed separately and turned on while configuring ImageMagick. NOTE: There is a possible bug of ImageMagick on OSX that multipages PDF can only be converted to one page PNG. The solution is to find imagegick/etc/delegates.xml to replace 'pngalpha' with 'pnmraw' (The detail is described at http://www.imagemagick.org/discourse-server/viewtopic.php?f=3&t=18001)
- lesscss
