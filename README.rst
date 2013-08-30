Chinchilla Frontend
===================

How to run
----------

1. Clone the repo
2. Make new virtualenv and activate it
3. cd cc_front
4. pip install -r requirement
5. cp src/cc/local_settings.py.sample src/cc/local_settings.py
6. Change the settings to match configuration in the local environment
7. ./src/cc/manage.py syncdb
8. ./src/cc/manage.py migrate
9. ./src/cc/manage.py runserver_plus


Other dependancies
------------------

- Redis
(TODO)