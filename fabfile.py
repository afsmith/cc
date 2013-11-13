from fabric.api import *

@task(alias='t')
def test():
    '''
    Executes test suite, optionally checking coverage.
    '''
    local('python manage.py test')


@task(alias='d')
def deploy_local():
    '''
    Deploy the latest changes to local envinronment
    '''
    local('git stash')
    local('git pull')
    local('pip install -r requirements.txt')
    local('python manage.py syncdb')
    local('python manage.py migrate')
    local('fab test')
    local('git stash apply')


@task(alias='r')
def runplus():
    '''
    Lazy shortcut for runserver_plus
    '''
    local('python manage.py runserver_plus')


@task(alias='s')
def shell():
    '''
    Another lazy shortcut for shell_plus
    '''
    local('python manage.py shell_plus')
