
from django.conf.urls.defaults import *

from cc.apps.tracking import views
urlpatterns = patterns('',
    url(r'^events/create/$', views.create_event, name='tracking-create_event'),
    url(r'^events/update/$', views.update_scorm_event, name='tracking-update_event'),
    url(r'^groups/(?P<group_id>\d+)/$', views.modules_with_tracking_ratio, name='tracking-modules_with_tracking_ration'),
    url(r'^modules/(?P<course_id>\d+)/segments/(?P<segment_id>\d+)/$', views.segment_history, name='tracking-segment-history'),
    url(r'^report_tracking/$', views.report_tracking, name='tracking-report_tracking'),
    url(r'^modules_usage/$', views.modules_usage, name='tracking-modules_usage'),
    url(r'^total_time/$', views.total_time, name='tracking-total_time'),
    url(r'^user_progress/$', views.user_progress, name='tracking-user_progress'),
    url(r'^user_page_progress/(?P<end_event_id>\d+)$', views.user_page_progress, name='tracking-user_page_progress'),
    url(r'^course_to_continue/$', views.course_to_continue, name='tracking-course_to_continue'),
)
