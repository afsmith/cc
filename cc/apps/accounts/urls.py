from django.conf.urls import patterns, url, include

from cc.apps.accounts.forms import UserCreationForm, UserPasswordResetForm
from registration.backends.default.views import RegistrationView

urlpatterns = patterns(
    '',
    url(r'^register/$',
        RegistrationView.as_view(form_class=UserCreationForm),
        name='accounts_register'),
    url(r'^login/$',
        'django.contrib.auth.views.login',
        name='auth_login'),
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='auth_logout'),
    url(r'^password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'password_reset_form': UserPasswordResetForm},
        name='auth_password_reset'),
    url(r'^invite/$',
        'cc.apps.accounts.views.invite',
        name='accounts_invite'),
    url(r'^remove_invitation/(?P<invitation_id>\d+)/$',
        'cc.apps.accounts.views.remove_invitation',
        name='remove_invitation'),
    url(r'^login_sso/$',
        'cc.apps.accounts.views.login_sso',
        name='login_sso'),    
    url(r'^token_sso/$',
        'cc.apps.accounts.views.token_sso',
        name='token_sso'),                                            
    url(r'', include('registration.backends.default.urls')),
)
