Chinchilla Frontend
===================

How to run
----------

1. Clone the repo
2. Make new virtualenv and activate it
3. cd cc_front
4. pip install -r requirement
5. cp cc/local_settings.py.sample cc/local_settings.py
6. Change the settings to match configuration in the local environment
7. python manage.py syncdb
8. python manage.py migrate
9. python manage.py runserver_plus


Other dependancies
------------------

- Redis
(TODO)