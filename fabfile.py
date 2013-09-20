from fabric.api import env, local
from fabric.operations import require
from fabric.utils import abort

import glob
import os
import subprocess

env.test_apps = ' '.join([
    'accounts',
    'cc',
    'cc_messages',
    'content',
    'tracking',
])

env.excludes = './tools/release/excludes'

# This will get overwritten by determine_version().
env.version = 'v0.1.0dev'


def test(coverage=False, only=None):
    """Executes test suite, optionally checking coverage.

    Accepted flags:
        - converage   Set to True to gather coverage information
                      (it is disable by default).
        - only        Name of an app/testcase/fixture you want to execute
                      (default includes all apps).

    Examples:
        % fab test:coverage=True
        % fab test:only=content

    The first example executes all tests and gathers coverage information. The
    second one executes only tests defined in the app with label ``content``.
    """

    if coverage:
        env._coverage = 'coverage run'
    else:
        env._coverage = ''

    if only:
        env.test_apps = only

    local('%(_coverage)s ./manage.py test %(test_apps)s' % env, capture=False)


def add2virtualenv():
    """Adds $CDW/cc to python path.
    """
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


def pylint(only_errors=False):
    """Runs pylint on all modules.
    """
    local(
        'pylint %s --rcfile docs/pylintrc cc/webfront cc/content'
        % ('-E' if only_errors else ''),
        capture=False
    )


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


def deploy_local():
    local('git pull --rebase')
    local('pip install -r requirements.txt')
    local('python manage.py syncdb')
    local('python manage.py migrate')
