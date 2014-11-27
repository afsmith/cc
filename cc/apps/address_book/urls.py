from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    'cc.apps.address_book.views',
    url(r'^$',
        views.AddressBookListView.as_view(),
        name='address_book_list'),
    url(r'^(?P<pk>\d+)/$',
        views.AddressBookUpdateView.as_view(),
        name='address_book_update'),
    url(r'^search/$',
        'search_contacts',
        name='search_contacts'),
    url(r'^import/$',
        'import_contacts',
        name='import_contacts'),
)
