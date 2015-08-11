from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    'cc.apps.api.views',
    url(r'^addcontact/$','addContact',name='addContact'),
    url(r'^sendemail/$','sendemail',name='sendemail'),
    url(r'^getreport/(?P<knetoSendId>\d*)$','getreport',name='getreport'),
)
