from fabric.api import (
    env, cd, prefix, sudo as _sudo, run as _run, hide, task, roles, local
)
from fabric.contrib.files import exists, upload_template
from fabric.colors import yellow, green, blue, red

from functools import wraps
from getpass import getpass, getuser
from glob import glob
from contextlib import contextmanager
from posixpath import join
import os
import re
import sys


################
# Config setup #
################

if len(env.roles) > 1:
    print "Sorry, only one roll at a time"
    exit()

conf = {}
if sys.argv[0].split(os.sep)[-1] in ("fab", "fab-script.py"):
    try:
        _tmp = __import__("cc.settings", globals(), locals(), ['FABRIC'], -1)
        conf = _tmp.FABRIC
        try:
            conf["ROLE_DEF"]
        except (KeyError, ValueError):
            raise ImportError
    except ImportError:
        print "Aborting, no host roles defined."
        exit()

if len(env.roles) == 1:
    env.db_pass = conf.get("DB_PASS", None)
    env.admin_pass = conf.get("ADMIN_PASS", None)
    env.user = conf.get("SSH_USER", getuser())
    env.password = conf.get("SSH_PASS", None)
    env.key_filename = conf.get("SSH_KEY_PATH", None)
    #env.hosts = conf.get("HOSTS", [])
    env.roledefs = conf.get("ROLE_DEF", [])

    env.proj_name = conf.get("PROJECT_NAME", os.getcwd().split(os.sep)[-1])
    env.venv_home = conf.get("VIRTUALENV_HOME", "/home/%s" % env.user)
    env.venv_path = "%s/%s" % (env.venv_home, env.proj_name)
    env.proj_dirname = "project"
    env.proj_path = "%s/%s" % (env.venv_path, env.proj_dirname)
    env.manage = "%s/bin/python %s/project/manage.py" % (
        env.venv_path, env.venv_path
    )

    env.repo_url = conf.get("REPO_URL", "")
    env.git = env.repo_url.startswith("git") or env.repo_url.endswith(".git")
    env.reqs_path = conf.get("REQUIREMENTS_PATH", None)
    env.gunicorn_port = conf.get("GUNICORN_PORT", 8000)
    env.locale = conf.get("LOCALE", "en_US.UTF-8")

    env.secret_key = conf.get("SECRET_KEY", "")
    env.nevercache_key = conf.get("NEVERCACHE_KEY", "")

    env.static_path = "%s/static" % env.venv_path

    env.live_host = conf.get("LIVE_HOSTNAME", {}).get(env.roles[0])
    env.live_key = conf.get("LIVE_KEY", {}).get(env.roles[0])
    env.live_cert = conf.get("LIVE_CERT", {}).get(env.roles[0])
    env.stripe_public_key = conf.get(
        "STRIPE_PUBLIC_KEY", {}
    ).get(env.roles[0], "")
    env.stripe_secret_key = conf.get(
        "STRIPE_SECRET_KEY", {}
    ).get(env.roles[0], "")


##################
# Template setup #
##################

# Each template gets uploaded at deploy time, only if their
# contents has changed, in which case, the reload command is
# also run.

templates = {
    "nginx": {
        "local_path": "deploy/nginx.conf",
        "remote_path": "/etc/nginx/sites-enabled/%(proj_name)s.conf",
        "reload_command": "service nginx restart",
    },
    "supervisor": {
        "local_path": "deploy/supervisor.conf",
        "remote_path": "/etc/supervisor/conf.d/%(proj_name)s.conf",
        "reload_command": "supervisorctl reload",
    },
    "cron": {
        "local_path": "deploy/crontab",
        "remote_path": "/etc/cron.d/%(proj_name)s",
        "owner": "root",
        "mode": "600",
    },
    "gunicorn": {
        "local_path": "deploy/gunicorn.conf.py",
        "remote_path": "%(proj_path)s/gunicorn.conf.py",
    },
    "settings": {
        "local_path": "deploy/live_settings.py",
        "remote_path": "%(proj_path)s/cc/local_settings.py",
    },
}


######################################
# Context for virtualenv and project #
######################################

@contextmanager
def virtualenv():
    """
    Runs commands within the project's virtualenv.
    """
    with cd(env.venv_path):
        with prefix("source %s/bin/activate" % env.venv_path):
            yield


@contextmanager
def project():
    """
    Runs commands within the project's directory.
    """
    with virtualenv():
        with cd(env.proj_dirname):
            yield


@contextmanager
def update_changed_requirements():
    """
    Checks for changes in the requirements file across an update,
    and gets new requirements if changes have occurred.
    """
    reqs_path = join(env.proj_path, env.reqs_path)
    get_reqs = lambda: run("cat %s" % reqs_path, show=False)
    old_reqs = get_reqs() if env.reqs_path else ""
    yield
    if old_reqs:
        new_reqs = get_reqs()
        if old_reqs == new_reqs:
            # Unpinned requirements should always be checked.
            for req in new_reqs.split("\n"):
                if req.startswith("-e"):
                    if "@" not in req:
                        # Editable requirement without pinned commit.
                        break
                elif req.strip() and not req.startswith("#"):
                    if not set(">=<") & set(req):
                        # PyPI requirement without version.
                        break
            else:
                # All requirements are pinned.
                return
        pip("-r %s/%s" % (env.proj_path, env.reqs_path))


###########################################
# Utils and wrappers for various commands #
###########################################

def _print(output):
    print
    print output
    print


def print_command(command):
    _print(blue("$ ", bold=True) +
           yellow(command, bold=True) +
           red(" ->", bold=True))


@roles()
@task
def run(command, show=True):
    """
    Runs a shell comand on the remote server.
    """
    if show:
        print_command(command)
    with hide("running"):
        return _run(command)


@roles()
@task
def sudo(command, show=True):
    """
    Runs a command as sudo.
    """
    if show:
        print_command(command)
    with hide("running"):
        return _sudo(command)


def log_call(func):
    @wraps(func)
    def logged(*args, **kawrgs):
        header = "-" * len(func.__name__)
        _print(green("\n".join([header, func.__name__, header]), bold=True))
        return func(*args, **kawrgs)
    return logged


def get_templates():
    """
    Returns each of the templates with env vars injected.
    """
    injected = {}
    for name, data in templates.items():
        injected[name] = dict([(k, v % env) for k, v in data.items()])
    return injected


def upload_template_and_reload(name):
    """
    Uploads a template only if it has changed, and if so, reload a
    related service.
    """
    template = get_templates()[name]
    local_path = template["local_path"]
    if not os.path.exists(local_path):
        project_root = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(project_root, local_path)
    remote_path = template["remote_path"]
    reload_command = template.get("reload_command")
    owner = template.get("owner")
    mode = template.get("mode")
    remote_data = ""
    if exists(remote_path):
        with hide("stdout"):
            remote_data = sudo("cat %s" % remote_path, show=False)
    with open(local_path, "r") as f:
        local_data = f.read()
        # Escape all non-string-formatting-placeholder occurrences of '%':
        local_data = re.sub(r"%(?!\(\w+\)s)", "%%", local_data)
        if "%(db_pass)s" in local_data:
            env.db_pass = db_pass()
        local_data %= env
    clean = lambda s: s.replace("\n", "").replace("\r", "").strip()
    if clean(remote_data) == clean(local_data):
        return
    upload_template(local_path, remote_path, env, use_sudo=True, backup=False)
    if owner:
        sudo("chown %s %s" % (owner, remote_path))
    if mode:
        sudo("chmod %s %s" % (mode, remote_path))
    if reload_command:
        sudo(reload_command)


def db_pass():
    """
    Prompts for the database password if unknown.
    """
    if not env.db_pass:
        env.db_pass = getpass("Enter the database password: ")
    return env.db_pass


@roles()
@task
def echo_hosts():
    """
    Prints list of hosts in group
    """
    return sudo("ifconfig -a")


@roles()
@task
def apt(packages):
    """
    Installs one or more system packages via apt.
    """
    return sudo("apt-get install -y -q " + packages)


@roles()
@task
def pip(packages):
    """
    Installs one or more Python packages within the virtual environment.
    """
    with virtualenv():
        return sudo("pip install %s" % packages)


def postgres(command):
    """
    Runs the given command as the postgres user.
    """
    show = not command.startswith("psql")
    return run("sudo -u root sudo -u postgres %s" % command, show=show)


@roles()
@task
def psql(sql, show=True):
    """
    Runs SQL against the project's database.
    """
    out = postgres('psql -c "%s"' % sql)
    if show:
        print_command(sql)
    return out


@roles()
@task
def backup(filename):
    """
    Backs up the database.
    """
    return postgres("pg_dump -Fc %s > %s" % (env.proj_name, filename))


@roles()
@task
def restore(filename):
    """
    Restores the database.
    """
    return postgres("pg_restore -c -d %s %s" % (env.proj_name, filename))


@roles()
@task
def python(code, show=True):
    """
    Runs Python code in the project's virtual environment, with Django loaded.
    """
    setup = "import os; os.environ['DJANGO_SETTINGS_MODULE']='cc.settings';"
    full_code = 'python -c "%s%s"' % (setup, code.replace("`", "\\\`"))
    with project():
        result = run(full_code, show=False)
        if show:
            print_command(code)
    return result


def static():
    """
    Returns the live STATIC_ROOT directory.
    """
    return python("from django.conf import settings;"
                  "print settings.STATIC_ROOT", show=False).split("\n")[-1]


@roles()
@task
def manage(command):
    """
    Runs a Django management command.
    """
    return run("%s %s" % (env.manage, command))


#########################
# Install and configure #
#########################
@roles()
@task
@log_call
def install():
    """
    Installs the base system and Python requirements for the entire server.
    """
    locale = "LC_ALL=%s" % env.locale
    with hide("stdout"):
        if locale not in sudo("cat /etc/default/locale"):
            sudo("update-locale %s" % locale)
            run("exit")
    sudo("apt-get update -y -q")
    apt("nginx libjpeg-dev python-dev python-setuptools git-core "
        "postgresql libpq-dev memcached supervisor redis-server "
        "libxtst-dev libx11-dev pkg-config")
    sudo("easy_install pip")
    sudo("pip install virtualenv")
    sudo("install -o %s -g %s -d /var/log/kneto/cc" % (env.user, env.user))


@roles()
@task
@log_call
def create():
    """
    Create a new virtual environment for a project.
    Pulls the project's repo from version control, adds system-level
    configs for the project, and initialises the database with the
    live host.
    """

    # Create virtualenv
    with cd(env.venv_home):
        if exists(env.proj_name):
            prompt = raw_input("\nVirtualenv exists: %s\nWould you like "
                               "to replace it? (yes/no) " % env.proj_name)
            if prompt.lower() != "yes":
                print "\nAborting!"
                return False
            remove()
        run("virtualenv %s --distribute" % env.proj_name)
        vcs = "git" if env.git else "hg"
        run("%s clone %s %s" % (vcs, env.repo_url, env.proj_path))

    # Create DB and DB user.
    pw = db_pass()
    user_sql_args = (env.proj_name, pw.replace("'", "\'"))
    user_sql = "CREATE USER %s WITH ENCRYPTED PASSWORD '%s';" % user_sql_args
    psql(user_sql, show=False)
    shadowed = "*" * len(pw)
    print_command(user_sql.replace("'%s'" % pw, "'%s'" % shadowed))
    psql("CREATE DATABASE %s WITH OWNER %s ENCODING = 'UTF8' "
         "LC_CTYPE = '%s' LC_COLLATE = '%s' TEMPLATE template0;" %
         (env.proj_name, env.proj_name, env.locale, env.locale))

    # Set up SSL certificate.
    conf_path = "/etc/nginx/conf"
    if not exists(conf_path):
        sudo("mkdir %s" % conf_path)
    with cd(conf_path):
        crt_file = env.proj_name + ".crt"
        key_file = env.proj_name + ".key"
        if not exists(crt_file) and not exists(key_file):
            try:
                crt_local, = glob(join("deploy", "*.crt"))
                key_local, = glob(join("deploy", "*.key"))
            except ValueError:
                parts = (env.live_cert, env.live_key, env.live_host)
                sudo("openssl req -new -x509 -nodes -out %s -keyout %s "
                     "-subj '/CN=%s' -days 3650" % parts)
            else:
                upload_template(crt_local, crt_file, use_sudo=True)
                upload_template(key_local, key_file, use_sudo=True)

    # setup static folder
    if not exists(env.static_path):
        run("mkdir %s" % env.static_path)

    # Set up project.
    upload_template_and_reload("settings")
    with project():
        if env.reqs_path:
            pip("-r %s/%s" % (env.proj_path, env.reqs_path))
        pip("gunicorn setproctitle south psycopg2 "
            "django-compressor python-memcached")
        manage("syncdb")
        manage("migrate")
        python("from django.conf import settings;"
               "from django.contrib.sites.models import Site;"
               "site, _ = Site.objects.get_or_create(id=settings.SITE_ID);"
               "site.domain = '" + env.live_host + "';"
               "site.save();")
#        if env.admin_pass:
#            pw = env.admin_pass
#            user_py = ("from mezzanine.utils.models import get_user_model;"
#                       "User = get_user_model();"
#                       "u, _ = User.objects.get_or_create(username='admin');"
#                       "u.is_staff = u.is_superuser = True;"
#                       "u.set_password('%s');"
#                       "u.save();" % pw)
#            python(user_py, show=False)
#            shadowed = "*" * len(pw)
#            print_command(user_py.replace("'%s'" % pw, "'%s'" % shadowed))

    return True


@roles()
@task
@log_call
def remove():
    """
    Blow away the current project.
    """
    if exists(env.venv_path):
        sudo("rm -rf %s" % env.venv_path)
    for template in get_templates().values():
        remote_path = template["remote_path"]
        if exists(remote_path):
            sudo("rm %s" % remote_path)
    psql("DROP DATABASE %s;" % env.proj_name)
    psql("DROP USER %s;" % env.proj_name)


##############
# Deployment #
##############
@roles()
@task
@log_call
def restart():
    """
    Restart gunicorn worker processes for the project.
    """
    pid_path = "%s/gunicorn.pid" % env.proj_path
    if exists(pid_path):
        sudo("kill -HUP `cat %s`" % pid_path)
    else:
        start_args = (env.proj_name, env.proj_name)
        sudo("supervisorctl start %s:gunicorn_%s" % start_args)
    sudo("supervisorctl restart celeryd")


@roles()
@task
@log_call
def deploy():
    """
    Deploy latest version of the project.
    Check out the latest version of the project from version
    control, install new requirements, sync and migrate the database,
    collect any new static assets, and restart gunicorn's work
    processes for the project.
    """
    if not exists(env.venv_path):
        prompt = raw_input("\nVirtualenv doesn't exist: %s\nWould you like "
                           "to create it? (yes/no) " % env.proj_name)
        if prompt.lower() != "yes":
            print "\nAborting!"
            return False
        create()
    for name in get_templates():
        upload_template_and_reload(name)
    with project():
        backup("last.db")
        static_dir = static()
        if exists(static_dir):
            run("tar -cf last.tar %s" % static_dir)
        git = env.git
        last_commit = "git rev-parse HEAD" if git else "hg id -i"
        run("%s > last.commit" % last_commit)
        with update_changed_requirements():
            run("git pull origin master -f" if git else "hg pull && hg up -C")
        manage("syncdb --noinput")
        manage("migrate --noinput")
        # compile LESS before collect static
        run("/opt/kneto/cc/project/compile-styles.sh")
        manage("collectstatic --clear --noinput")

    restart()
    return True


@roles()
@task
@log_call
def rollback():
    """
    Reverts project state to the last deploy.
    When a deploy is performed, the current state of the project is
    backed up. This includes the last commit checked out, the database,
    and all static files. Calling rollback will revert all of these to
    their state prior to the last deploy.
    """
    with project():
        with update_changed_requirements():
            update = "git checkout" if env.git else "hg up -C"
            run("%s `cat last.commit`" % update)
        with cd(join(static(), "..")):
            run("tar -xf %s" % join(env.proj_path, "last.tar"))
        restore("last.db")
    restart()


@roles()
@task
@log_call
def all():
    """
    Installs everything required on a new system and deploy.
    From the base software, up to the deployed project.
    """
    install()
    if create():
        deploy()


# ------------------------------ Local tasks ------------------------------ #
@task(alias='t')
def test(mode=''):
    '''
    Executes test suite
    fab t => run ALL tests
    fab t:n => run normal tests
    fab t:s => run selenium tests
    '''
    if mode == 's':
        local('python manage.py test --where=cc/selenium_tests/')
    elif mode == 'n':
        local('python manage.py test --where=cc/apps/')
    else:
        local('python manage.py test')


@task(alias='dl')
def deploy_local():
    '''
    Deploy the latest changes to local envinronment
    '''
    local('git stash')
    local('git pull')
    local('pip install -r requirements.txt')
    local('python manage.py syncdb')
    local('python manage.py migrate')
    local('git stash apply')


@task(alias='r')
def runplus():
    '''
    Lazy shortcut for runserver_plus
    '''
    local('python manage.py runserver_plus 0.0.0.0:8258')


@task(alias='s')
def shell():
    '''
    Another lazy shortcut for shell_plus
    '''
    local('python manage.py shell_plus')


@task(alias='cdb')
def cleanup_db():
    '''
    Clean up the current development DB
    '''
    local(
        'echo "TRUNCATE cc_messages_message, cc_messages_message_files, '
        'cc_messages_message_receivers, reports_bounce, tracking_closeddeal, '
        'tracking_trackingevent, tracking_trackingsession, '
        'tracking_trackinglog CASCADE;" | python manage.py dbshell'
    )
