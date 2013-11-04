from django.contrib.auth import decorators as auth_decorators

from annoying.decorators import render_to


@auth_decorators.login_required
@render_to('main/dashboard.html')
def dashboard(request):
    return {}
