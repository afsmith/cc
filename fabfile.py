from fabric.api import *
from fabric.operations import require
from fabric.utils import abort

import glob
import os
import subprocess

env.excludes = './tools/release/excludes'

# This will get overwritten by determine_version().
env.version = 'v0.1.0dev'


def add2virtualenv():
    '''
    Adds $CDW/cc to python path.
    '''
    env_path = os.environ.get('VIRTUAL_ENV', None)
    if env_path is None:
        abort('Virtual env is not active.')

    path = [env_path]
    path.extend('lib/python2.?/site-packages'.split('/'))
    path = os.path.join(*path)
    # there should be only one matching path
    path = glob.glob(path)[0]
    path = os.path.join(path, 'cc.pth')

    with open(path, 'wb') as fh:
        fh.write(os.path.join(os.path.abspath(env.cwd), 'src'))


def release():
    determine_version()
    create_tarball()


def determine_version():
    version = subprocess.check_output([
        "git", "describe", "--match", "v[0-9]*", "--abbrev=4", "HEAD"
    ]).rstrip()
    local('git update-index -q --refresh')
    is_dirty = subprocess.check_output([
        "git", "diff-index", "--name-only", "HEAD", "--"
    ]).rstrip()

    if is_dirty:
        version += '-dirty'
    version = version.replace('-', '.')
    # strip the starting "v"
    version = version[1:]

    env.version = version
    env.pkg_name = 'cc-%(version)s' % env


def create_tarball():
    require('version', provided_by=['determine_version'])

    local(
        'git archive --format=tar --prefix=%(pkg_name)s/ HEAD | tar xf -' % env,
        capture=False
    )

    local('python ./tools/virtualenv.py %(pkg_name)s/ENV' % env)
    local(
        '%(pkg_name)s/ENV/bin/pip install -r %(pkg_name)s/requirements.txt'
        % env
    )
    local('python ./tools/virtualenv.py --relocatable %(pkg_name)s/ENV' % env)

    local('cp %(excludes)s %(excludes)s.tmp' % env)
    local('sed -i -r -e "s!^\./!%(pkg_name)s/!g" %(excludes)s.tmp' % env)
    local('mkdir _build')
    local(
        'tar zcf _build/%(pkg_name)s.tar.gz -X%(excludes)s.tmp %(pkg_name)s'
        % env
    )
    local('rm %(excludes)s.tmp' % env)


### ------------------------- Tasks with aliases ------------------------- ###
@task(alias='t')
def test(coverage=False, only=None):
    '''
    Executes test suite, optionally checking coverage.

    Accepted flags:
        - converage   Set to True to gather coverage information
                      (it is disable by default).
        - only        Name of an app/testcase/fixture you want to execute
                      (default includes all apps).

    Examples:
        fab test:coverage=True
        fab test:only=content

    The first example executes all tests and gathers coverage information. The
    second one executes only tests defined in the app with label ``content``.
    '''

    test_apps = ' '.join([
        'accounts',
        'cc_messages',
        'content',
        'tracking',
    ])

    if coverage:
        _coverage = 'coverage run'
    else:
        _coverage = ''

    if only:
        test_apps = only

    local('%s ./manage.py test %s' % (_coverage, test_apps), capture=False)


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
    local('git stash apply')  # apply the stash after successful deploying


@task(alias='r')
def run():
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

