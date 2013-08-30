# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Tests.
"""

from __future__ import absolute_import

import json, StringIO, datetime, urlparse
from xml.parsers import expat

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import User
from django.core.files import storage
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.test import client, TestCase
from elementtree import ElementTree as ET
import os
from administration.models import ConfigEntry
from cc.apps.content.convert import VideoConverter
from cc.apps.content.models import Segment, File

from management import models as mgmnt_models
from plato_common.test_utils import ClientTestCase

from cc.apps.content import convert, models, serializers, utils, tasks, course_states
from cc.apps.content.course_states import Draft, Active, ActiveAssign, Deactivated, ActiveInUse, DeactivatedUsed


class ListModulesTest(ClientTestCase):
    fixtures = ('sample.json', 'test-course.json', 'test-tags.json', 'test-users-content.json',)
    url = '/content/'

    def test_get_requires_logged_in_user(self):
        c = client.Client()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_get_request_returns_302_for_user(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 302)
    
    def test_get_request_returns_admins_groups_list(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertTrue('groups' in response.context)
        self.assertTrue('my_groups' in response.context)
        all_groups = auth_models.Group.objects.all().count()
        self.assertNotEquals(len(response.context['groups']), all_groups)

    def test_forms_in_context(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertTrue('form' in response.context)
        self.assertTrue('manageModulesForm' in response.context)

    def test_get_request_returns_all_groups(self):
        c = self._get_client_superadmin()
        all_groups = auth_models.Group.objects.all().count()
        response = c.get(self.url)
        self.assertEquals(len(response.context['groups']), all_groups)

    def test_get_uses_correct_template(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'content/list_modules.html')

    def test_post(self):
        c = self._get_client_admin()
        response = c.post(self.url,
                  json.dumps({'module_id': '1',
                              "title": "title",
                              "objective": "objective",
                              "language": "10",
                              "expires_on": "2010-12-12",
                              "groups_ids": [1],
                              'allow_download': 'True',
                              'allow_skipping': 'True',
                              'sign_off_required': 'True'}),
                  content_type='application/json')
        data = json.loads(response.content)
        self.assertEquals(data['status'], "OK")
        course = models.Course.objects.get(id=1)
        self.assertEquals(course.title, "title")
        self.assertEquals(course.groups_can_be_assigned_to.all().count(), 1)
        self.assertEquals(course.language, "10")
        self.assertEquals(course.objective, "objective")
        self.assertEquals(course.allow_download, True)
        self.assertEquals(course.sign_off_required, True)

    def test_post_without_expires_on_date(self):
        c = self._get_client_admin()
        response = c.post(self.url,
                  json.dumps({'module_id': '1',
                              "title": "title",
                              "objective": "objective",
                              "language": "10",
                              "groups_ids": [1],
                              'allow_download': 'True',
                              'allow_skipping': 'True',
                              "sign_off_required": 'True'}),
                  content_type='application/json')
        data = json.loads(response.content)
        self.assertEquals(data['status'], "OK")

class ModulesAssignTest(ClientTestCase):

    fixtures = ('test-users-content.json',)
    url = '/content/modules/assign/'

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_request_returns_200(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_uses_correct_template(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'content/module_assignment.html')
        

class FindFilesWithEmptyDatabaseTest(ClientTestCase):
    """Exercises find_files view when databases is empty.
    """
    fixtures = ('test-users-content.json',)

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.get('/content/files/')
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get('/content/files/')
        self.assertEquals(response.status_code, 200)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.get('/content/files/')
        self.assertEquals(response.status_code, 200)

    def _get_files(self, url='/content/files/'):
        c = self._get_client_admin()
        response = c.get(url)
        return json.loads(response.content)

    def test_files_search_returns_empty_list(self):
        files = self._get_files()
        self.assertEquals(len(files['entries']), 0)

    def test_files_search_returns_code_200(self):
        c = self._get_client_admin()
        response = c.get('/content/files/')
        self.assertEquals(response.status_code, 200)

    def test_response_contains_meta_section(self):
        files = self._get_files()
        self.assertTrue(u'meta' in files)

    def test_response_contains_entries_section(self):
        files = self._get_files()
        self.assertTrue(u'entries' in files)

    def test_no_next_page_url(self):
        files = self._get_files()
        self.assertFalse(u'next-page-url' in files['meta'])

    def test_has_curr_page_url(self):
        files = self._get_files()
        self.assertTrue(u'curr-page-url' in files['meta'])

    def test_no_prev_page_url(self):
        files = self._get_files()
        self.assertFalse(u'prev-page-url' in files['meta'])

    def test_curr_page_is_1(self):
        files = self._get_files()
        self.assertEquals(files['meta']['curr-page'], 1)

    def test_total_pages_is_1(self):
        files = self._get_files()
        self.assertEquals(files['meta']['total-pages'], 1)

    def test_file_title_is_escaped_to_prevent_xss(self):
        c = self._get_client_superadmin()
        
        unsafe_title = '<escape-this/>'

        f = models.File(
            title=unsafe_title,
            type=models.File.TYPE_IMAGE,
            orig_filename='foo.jpeg',
            expires_on=datetime.date.today()+datetime.timedelta(weeks=2),
            language='en',
            status=models.File.STATUS_AVAILABLE)
        f.save()

        response = c.get('/content/files/')
        data =  json.loads(response.content)

        self.assertNotEquals(data['entries'][0]['title'], unsafe_title)
        f.delete()


class FindFilesWithSampleDatabaseTest(ClientTestCase):
    """Exercises find_files view with sample data in database.
    """

    fixtures = ('sample.json','test-users-content.json',)

    def setUp(self):
        self._orig_size = settings.CONTENT_PAGE_SIZE
        settings.CONTENT_PAGE_SIZE = 10

    def tearDown(self):
        settings.CONTENT_PAGE_SIZE = self._orig_size

    def _assertGreater(self, a, b):
        if a <= b:
            raise AssertionError('%d <= %d' % (a, b))

    def _get_files(self, url='/content/files/'):
        c = self._get_client_admin()
        response = c.get(url)
        return json.loads(response.content)

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.get('/content/files/')
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get('/content/files/')
        self.assertEquals(response.status_code, 200)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.get('/content/files/')
        self.assertEquals(response.status_code, 200)

    def test_returns_correct_value_for_total_pages(self):
        files = self._get_files()
        self.assertEquals(files['meta']['total-pages'], 3)

    def test_newest_page_does_not_have_next_link(self):
        files = self._get_files('/content/files/?page=1')
        self.assertTrue('next-page-url' in files['meta'])

    def test_oldest_page_does_not_have_prev_link(self):
        files = self._get_files('/content/files/?page=2')
        self.assertTrue('prev-page-url' in files['meta'])

    def test_non_extreme_page_has_prev_link(self):
        files = self._get_files('/content/files/?page=2')
        self.assertTrue('prev-page-url' in files['meta'])

    def test_non_extreme_page_has_next_link(self):
        files = self._get_files('/content/files/?page=1')
        self.assertTrue('next-page-url' in files['meta'])

    def test_has_curr_page_url(self):
        files = self._get_files()
        self.assertTrue(u'curr-page-url' in files['meta'])

    def test_curr_page_url_is_accessible(self):
        page = self._get_files()
        c = self._get_client_admin()
        response = c.get(page['meta']['curr-page-url'])
        self.assertEquals(response.status_code, 200)

    def test_next_page_link_returns_existing_page(self):
        curr_page = self._get_files('/content/files/?page=1')
        next_page_url = curr_page['meta']['next-page-url']
        c = self._get_client_admin()
        response = c.get(next_page_url)
        self.assertEquals(response.status_code, 200)

    def test_prev_page_link_returns_existing_page(self):
        curr_page = self._get_files('/content/files/?page=2')
        prev_page_url = curr_page['meta']['prev-page-url']
        c = self._get_client_admin()
        response = c.get(prev_page_url)
        self.assertEquals(response.status_code, 200)

    def test_next_page_link_returns_correct_page(self):
        curr_page = self._get_files('/content/files/?page=1')
        curr_page_num = curr_page['meta']['curr-page']
        next_page_url = curr_page['meta']['next-page-url']
        next_page = self._get_files(next_page_url)
        next_page_num = next_page['meta']['curr-page']
        self.assertEquals(curr_page_num + 1, next_page_num)

    def test_next_page_link_contains_tags_ids(self):
        curr_page = self._get_files('/content/files/?page=1')
        next_page_url = curr_page['meta']['next-page-url']
        self.assertTrue(next_page_url.find('tags_ids'))

    def test_next_page_link_contains_language(self):
        curr_page = self._get_files('/content/files/?page=1')
        next_page_url = curr_page['meta']['next-page-url']
        self.assertTrue(next_page_url.find('language'))

    def test_next_page_link_contains_file_name(self):
        curr_page = self._get_files('/content/files/?page=1')
        next_page_url = curr_page['meta']['next-page-url']
        self.assertTrue(next_page_url.find('file_name'))

    def test_next_page_link_contains_file_type(self):
        curr_page = self._get_files('/content/files/?page=1')
        next_page_url = curr_page['meta']['next-page-url']
        self.assertTrue(next_page_url.find('file_type'))

    def test_prev_page_link_returns_correct_page(self):
        curr_page = self._get_files('/content/files/?page=2')
        curr_page_num = curr_page['meta']['curr-page']
        prev_page_url = curr_page['meta']['prev-page-url']
        prev_page = self._get_files(prev_page_url)
        prev_page_num = prev_page['meta']['curr-page']
        self.assertEquals(curr_page_num - 1, prev_page_num)

    def test_prev_page_link_contains_tags_ids(self):
        curr_page = self._get_files('/content/files/?page=2')
        prev_page_url = curr_page['meta']['prev-page-url']
        self.assertTrue(prev_page_url.find('tags_ids'))

    def test_prev_page_link_contains_language(self):
        curr_page = self._get_files('/content/files/?page=2')
        prev_page_url = curr_page['meta']['prev-page-url']
        self.assertTrue(prev_page_url.find('language'))

    def test_prev_page_link_contains_file_name(self):
        curr_page = self._get_files('/content/files/?page=2')
        prev_page_url = curr_page['meta']['prev-page-url']
        self.assertTrue(prev_page_url.find('file_name'))

    def test_prev_page_link_contains_file_type(self):
        curr_page = self._get_files('/content/files/?page=2')
        prev_page_url = curr_page['meta']['prev-page-url']
        self.assertTrue(prev_page_url.find('file_type'))

    def test_default_page_is_last_one(self):
        files = self._get_files('/content/files/')
        self.assertEquals(files['meta']['curr-page'], 3)

    def test_response_contains_meta_section(self):
        files = self._get_files()
        self.assertTrue(u'meta' in files)

    def test_response_contains_entries_section(self):
        files = self._get_files()
        self.assertTrue(u'entries' in files)

    def test_files_contain_id_attribute(self):
        files = self._get_files()
        f = files['entries'][0]
        self.assertTrue(u'id' in f)

    def test_files_contain_type_attribute(self):
        files = self._get_files()
        f = files['entries'][0]
        self.assertTrue(u'type' in f)

    def test_files_contain_url_attribute(self):
        files = self._get_files()
        f = files['entries'][0]
        self.assertTrue(u'url' in f)

    def test_files_contain_title_attribute(self):
        files = self._get_files()
        f = files['entries'][0]
        self.assertTrue(u'title' in f)

    def test_files_contain_created_on_attribute(self):
        files = self._get_files()
        f = files['entries'][0]
        self.assertTrue(u'created_on' in f)

    def test_files_contain_expires_on_attribute(self):
        files = self._get_files()
        f = files['entries'][0]
        self.assertTrue(u'expires_on' in f)

    def test_files_contain_thumbnail_url_attribute(self):
        files = self._get_files()
        f = files['entries'][0]
        self.assertTrue(u'thumbnail_url' in f)

    def test_files_contain_is_removable_attribute(self):
        files = self._get_files()
        f = files['entries'][0]
        self.assertTrue(u'is_removable' in f)

    def test_without_page_returns_latest_page(self):
        files = self._get_files()
        self.assertEquals(files['entries'][0]['id'], 28)

    def test_latest_page_is_full_if_possible(self):
        files = self._get_files()
        self.assertEquals(len(files['entries']), 10)

    def test_elements_are_in_descending_order(self):
        files = self._get_files()
        self._assertGreater(files['entries'][0]['id'], files['entries'][-1]['id'])

    def test_requesting_negative_page_number_returns_404(self):
        c = self._get_client_admin()
        response = c.get('/content/files/?page=-1')
        self.assertEquals(response.status_code, 404)

    def test_requesting_zero_page_returns_404(self):
        c = self._get_client_admin()
        response = c.get('/content/files/?page=-1')
        self.assertEquals(response.status_code, 404)

    def test_requesting_non_numeric_page_number_returns_404(self):
        c = self._get_client_admin()
        response = c.get('/content/files/?page=asdf')
        self.assertEquals(response.status_code, 404)

    def test_not_giving_page_number_returns_404(self):
        c = self._get_client_admin()
        response = c.get('/content/files/?page=')
        self.assertEquals(response.status_code, 404)

    def test_requesting_non_existing_page_number_returns_404(self):
        c = self._get_client_admin()
        response = c.get('/content/files/?page=100')
        self.assertEquals(response.status_code, 404)


class FindFilesTest(ClientTestCase):
    """Exercises find_files view with sample data in database.
    """

    fixtures = ('sample.json', 'test-tags.json', 'test-users-content.json',)
    url = "/content/files/?page=1&tags_ids=%s&language=%s&file_name=%s&file_type=%s"

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.get(self.url % ("RICE", "", "", ""))
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url % ("RICE", "", "", ""))
        self.assertEquals(response.status_code, 200)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.get(self.url % ("RICE", "", "", ""))
        self.assertEquals(response.status_code, 200)

    def test_should_return_by_two_tags(self):
        c = self._get_client_admin()
        response = c.get(self.url % ("PASTA,POTATOES", "", "", ""))
        files = json.loads(response.content)
        self.assertEquals(len(files['entries']), 2)

    def test_should_return_by_one_tag(self):
        c = self._get_client_admin()
        response = c.get(self.url % ("RICE", "", "", ""))
        files = json.loads(response.content)
        self.assertEquals(len(files['entries']), 1)

    def test_should_return_all_files(self):
        c = self._get_client_admin()
        response = c.get(self.url % ("", "", "", ""))
        files = json.loads(response.content)
        self.assertEquals(len(files['entries']), 8)

    def test_returns_by_language(self):
        c = self._get_client_admin()
        response = c.get(self.url % ("", "10", "", ""))
        files = json.loads(response.content)
        self.assertEquals(len(files['entries']), 5)

    def test_returns_by_file_name(self):
        c = self._get_client_admin()
        response = c.get(self.url % ("", "", "Praesent", ""))
        files = json.loads(response.content)
        self.assertEquals(len(files['entries']), 1)

    def test_returns_by_file_type(self):
        c = self._get_client_admin()
        response = c.get(self.url % ("", "", "", models.File.TYPE_PLAIN))
        files = json.loads(response.content)
        self.assertEquals(len(files['entries']), 2)


class ImportFileTest(ClientTestCase):
    """Exercises import_file view.
    """
    fixtures = ('test-users-content.json',)
    url = '/content/import/'

    def setUp(self):
        self._storage = FakeStorage()
        self._orig_storage = storage.default_storage
        storage.default_storage = self._storage
        self._FILE_UPLOAD_MAX_MEMORY_SIZE = settings.FILE_UPLOAD_MAX_MEMORY_SIZE

    def tearDown(self):
        storage.default_storage = self._orig_storage
        settings.FILE_UPLOAD_MAX_MEMORY_SIZE = self._FILE_UPLOAD_MAX_MEMORY_SIZE

    def _get_fh(self, size=1024):
        f = StringIO.StringIO('A' * size)
        f.name = 'bar.jpg'
        return f

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_get_method_returns_import_form(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'content/module_content.html')
        self.assertTrue('dms_enabled' in response.context)

    def test_invalid_form_post_returns_form(self):
        c = self._get_client_admin()
        response = c.post(self.url)
        data = json.loads(response.content)
        self.assertEquals(data['status'], "ERROR")

    def test_on_post_file_is_required(self):
        c = self._get_client_admin()
        response = c.post(self.url, {})
        data = json.loads(response.content)
        self.assertEquals(data['status'], "ERROR")

    def test_on_post_success_redirects_to_confirmation_page(self):
        c = self._get_client_admin()
        f = self._get_fh()
        response = c.post(self.url, {'file': f})
        f.close()
        data = json.loads(response.content)
        self.assertEquals(data['status'], "OK")

    def test_on_success_should_add_default_tag_with_username(self):
        c = self._get_client_admin()
        f = self._get_fh()
        response = c.post(self.url, {'file': f})
        f.close()
        data = json.loads(response.content)
        self.assertEquals(data['status'], "OK")
        models.File.objects.get(id=data['file_id'], tag__name="ADMIN", tag__is_default=True)

    def test_on_success_should_return_is_duration_visible_attr(self):
        c = self._get_client_admin()
        f = self._get_fh()
        response = c.post(self.url, {'file': f})
        f.close()
        data = json.loads(response.content)
        self.assertTrue("is_duration_visible" in data)
        
    def test_upload_of_file_without_ext_results_in_error(self):
        c = self._get_client_admin()
        f = self._get_fh()
        f.name = 'no-extension-here'
        response = c.post(self.url, {'file': f})
        f.close()
        data = json.loads(response.content)
        self.assertEquals(data['status'], "ERROR")

    def test_upload_of_file_with_unknown_ext_results_in_error(self):
        c = self._get_client_admin()
        f = self._get_fh()
        f.name = 'foo.unknown-extension'
        response = c.post(self.url, {'file': f})
        f.close()
        data = json.loads(response.content)
        self.assertEquals(data['status'], "ERROR")

    def test_adds_imported_file_to_database(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        self.assertEquals(models.File.objects.all().count(), 1)

    #
    # XXX: I've disabled this test for now as we don't have any way to skip
    #      conversion and it is eager (read: blocking) when tests are run.
    #      That means there is no chance we can see files with UPLOADED
    #      status. -- BOL
    #
    def _test_new_files_are_in_uploaded_status(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        f = models.File.objects.all()[0]
        self.assertEquals(f.status, models.File.STATUS_UPLOADED)

    def test_stores_original_filename_of_uploaded_files(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        f2 = models.File.objects.all()[0]
        self.assertEquals(f2.orig_filename, f.name)

    def test_uploaded_files_get_assigned_unique_key(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        f = models.File.objects.all()[0]
        self.assertTrue(isinstance(f.key, basestring))
        self.assertTrue(len(f.key))

    def test_stores_file_after_upload_using_key_and_ext(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        f2 = models.File.objects.all()[0]
        self.assertEquals(self._storage.last_filename, f2.orig_file_path)

    def test_writes_all_content_to_file(self):
        size = (1024 ** 2)
        c = self._get_client_admin()
        f = self._get_fh(size=size)
        c.post(self.url, {'file': f})
        f.close()
        self.assertEquals(self._storage.last_buf.size, size)
    
    def test_should_not_write_content_reached_max_upload_size(self):
        size = (1024 ** 2) * 11 
        settings.FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 ** 2
        c = self._get_client_admin()
        f = self._get_fh(size=size)
        c.post(self.url, {'file': f})
        f.close()
        self.assertFalse(self._storage.last_buf)

    def test_closes_file_after_write(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        self.assertTrue(self._storage.last_buf.closed)


class CreateModuleViewTest(ClientTestCase):
    """Exercises create_module view.
    """

    fixtures = ('test-users-content.json',)
    url = '/content/create/'

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_renders_correct_template(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'content/module_creator.html')

class CopyModuleViewTest(ClientTestCase):
    """Exercises copy_module view.
    """

    fixtures = ('test-users-content.json','sample.json','test-course.json',)
    url = '/content/copy/%d/'
    redirect_url = 'content/create/%d/'

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.get(self.url%1)
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url%1)
        self.assertRedirects(response, self.redirect_url%301)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.get(self.url%1)
        self.assertRedirects(response, self.redirect_url%301)

    def test_non_existing_course_returns_404(self):
        c = self._get_client_admin()
        response = c.get(self.url%12345)
        self.assertEquals(response.status_code, 404)


class ModuleSignOffButtonTest(ClientTestCase):
    """Exercises module_descr view.
    """

    fixtures = ('test-course-sign-off.json','test-users-content.json',
            'test-tracking-sign-off.json')
    url = '/content/show-sign-off-button/%s/'

    def test_does_not_accept_anonymous_user(self):
        c = client.Client()
        response = c.get(self.url % 300)
        self.assertEquals(response.status_code, 302)

    def test_accepts_logged_in_user(self):
        c = self._get_client_user()
        response = c.get(self.url % 300)
        self.assertEquals(response.status_code, 200)

    def test_requesting_module_with_invalid_id_returns_404(self):
        c = self._get_client_user()
        response = c.get(self.url % 'asd')
        self.assertEquals(response.status_code, 404)

    def test_requesting_nonexistent_module_id_returns_404(self):
        c = self._get_client_user()
        response = c.get(self.url % 303)
        self.assertEquals(response.status_code, 404)

    def test_requesting_module_finished_ok(self):
        c = self._get_client_user()
        response = c.get(self.url % 300)
        self.assertEquals(response.status_code, 200)
        try:
            data = json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')
        self.assertEquals(data['status'], 'OK')
        self.assertEquals(data['show'], True)

    def test_requesting_module_disabled_sign_off(self):
        c = self._get_client_user()
        response = c.get(self.url % 301)
        self.assertEquals(response.status_code, 200)
        try:
            data = json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')
        self.assertEquals(data['status'], 'OK')
        self.assertEquals(data['show'], False)

    def test_requesting_module_not_finished(self):
        c = self._get_client_user()
        response = c.get(self.url % 302)
        self.assertEquals(response.status_code, 200)
        try:
            data = json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')
        self.assertEquals(data['status'], 'OK')
        self.assertEquals(data['show'], False)

    def test_requesting_module_not_allowed(self):
        c = self._get_client_user()
        response = c.get(self.url % 2)
        self.assertEquals(response.status_code, 200)
        try:
            data = json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')
        self.assertEquals(data['status'], 'ERROR')
        self.assertEquals(data['error'], 'User is not allowed to view this content.')


class ModuleSignOffTest(ClientTestCase):
    """Exercises module_descr view.
    """

    fixtures = ('test-course-sign-off.json','test-users-content.json',
            'test-tracking-sign-off.json')
    url = '/content/sign-off/%s/'

    def test_does_not_accept_anonymous_user(self):
        c = client.Client()
        response = c.get(self.url % 300)
        self.assertEquals(response.status_code, 302)

    def test_requesting_module_with_invalid_id_returns_404(self):
        c = self._get_client_user()
        response = c.get(self.url % 'asd')
        self.assertEquals(response.status_code, 404)

    def test_requesting_nonexistent_module_id_returns_404(self):
        c = self._get_client_user()
        response = c.get(self.url % 303)
        self.assertEquals(response.status_code, 404)

    def test_requesting_module_finished_ok(self):
        c = self._get_client_user()
        response = c.get(self.url % 300)
        self.assertEquals(response.status_code, 200)
        try:
            data = json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')
        self.assertEquals(data['status'], 'OK')
        course_user = models.CourseUser.objects.get(user__id=3, course__id=300)
        self.assertEquals(course_user.sign_off, True)

    def test_requesting_module_disabled_sign_off(self):
        c = self._get_client_user()
        response = c.get(self.url % 301)
        self.assertEquals(response.status_code, 200)
        try:
            data = json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')
        self.assertEquals(data['status'], 'ERROR')
        self.assertEquals(data['error'], 'Module does not have sign off option')

    def test_requesting_module_not_finished(self):
        c = self._get_client_user()
        response = c.get(self.url % 302)
        self.assertEquals(response.status_code, 200)
        try:
            data = json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')
        self.assertEquals(data['status'], 'ERROR')
        self.assertEquals(data['error'], 'Module is not finished yet.')

    def test_requesting_module_not_allowed(self):
        c = self._get_client_user()
        response = c.get(self.url % 2)
        self.assertEquals(response.status_code, 200)
        try:
            data = json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')
        self.assertEquals(data['status'], 'ERROR')
        self.assertEquals(data['error'], 'User is not allowed to view this content.')


class ModuleDescrViewTest(ClientTestCase):
    """Exercises module_descr view.
    """

    fixtures = ('test-course.json','test-users-content.json',)
    url = '/content/modules/%s/'

    def test_does_not_accept_anonymous_user(self):
        c = client.Client()
        response = c.get(self.url % 300)
        self.assertEquals(response.status_code, 302)

    def test_accepts_logged_in_user(self):
        c = self._get_client_user()
        response = c.get(self.url % 300)
        self.assertEquals(response.status_code, 200)

    def test_requesting_module_with_invalid_id_returns_404(self):
        c = self._get_client_user()
        response = c.get(self.url % 'asd')
        self.assertEquals(response.status_code, 404)

    def test_requesting_nonexistent_module_id_returns_404(self):
        c = self._get_client_user()
        response = c.get(self.url % 303)
        self.assertEquals(response.status_code, 404)

    def test_requesting_existing_module_id_returns_200(self):
        c = self._get_client_user()
        response = c.get(self.url % 300)
        self.assertEquals(response.status_code, 200)

    def test_default_response_type_is_json(self):
        c = self._get_client_user()
        response = c.get(self.url % 300)
        try:
            json.loads(response.content)
        except ValueError, e:
            self.fail('Failed processing module descr (expected JSON format).')

    def test_requesting_format_json_returns_json(self):
        c = self._get_client_user()
        response = c.get((self.url % 300)+'?format=json')
        try:
            json.loads(response.content)
        except ValueError:
            self.fail('Failed processing module descr (expected JSON format).')

    def test_requesting_format_xml_returns_xml(self):
        c = self._get_client_user()
        response = c.get((self.url % 300)+'?format=xml')
        try:
            expat.ParserCreate().Parse(response.content)
        except ValueError:
            self.fail('Failed processing module descr (expected XML format).')

    def test_returns_404_for_unknown_format(self):
        c = self._get_client_user()
        response = c.get((self.url % 300)+'?format=foobar')
        self.assertEquals(response.status_code, 404)

    def test_course_title_and_objective_are_escaped_to_prevent_xss(self):
        unsafe_title = '<escape/>'
        unsafe_objective = 'also <escape/> this'
        course = models.Course(
            title=unsafe_title,
            objective=unsafe_objective,
            owner=User.objects.get(id=1))
        course.save()
        c = self._get_client_user()
        response = c.get(self.url % course.id)
        data = json.loads(response.content)
        self.assertNotEquals(data['meta']['title'], unsafe_title)
        self.assertNotEquals(data['meta']['objective'], unsafe_objective)

    def test_title_of_a_course_segment_is_escaped_to_prevent_xss(self):
        course = models.Course(title='foobar', owner=User.objects.get(id=1))
        course.save()

        unsafe_title = '<escape-this/>'
        f = models.File(
            title=unsafe_title,
            type=models.File.TYPE_IMAGE,
            orig_filename='foo.jpeg',
            expires_on=datetime.date.today() + datetime.timedelta(weeks=2),
            language='en')
        f.save()

        s = models.Segment(file=f, course=course, track=0, start=1, end=1)
        s.save()

        c = self._get_client_user()
        response = c.get(self.url % course.id)
        data = json.loads(response.content)
        self.assertNotEquals(data['track0'][0]['title'], unsafe_title)


class FilesManageViewTest(ClientTestCase):
    """Exercises files_manage view.
    """

    fixtures = ('test-users-content.json',)
    url = '/content/manage/'

    def test_renders_correct_template(self):
        c = self._get_client_admin()
        c.login(username='admin', password='admin')
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'content/files_manage.html')

    def test_non_admin_users_do_not_have_access(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    def test_admin_users_have_access(self):
        c = self._get_client_admin()
        c.login(username='admin', password='admin')
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'content/files_manage.html')


class FileModelTest(ClientTestCase):
    """Tests the File model.
    """

    def test_type_from_name_raises_exception_if_unknown_extension(self):
        try:
            models.File.type_from_name('foo.bah')
            self.fail('Exception UnsupportedFileTypeError not risen.')
        except utils.UnsupportedFileTypeError:
            pass

    def test_type_from_name_raises_exception_if_no_extension(self):
        try:
            models.File.type_from_name('foo')
            self.fail('Exception UnsupportedFileTypeError not risen.')
        except utils.UnsupportedFileTypeError:
            pass

    def test_type_from_name_raises_exception_if_no_extension_after_delimeter(self):
        try:
            models.File.type_from_name('foo.')
            self.fail('Exception UnsupportedFileTypeError not risen.')
        except utils.UnsupportedFileTypeError:
            pass

    def test_type_from_name_correctly_regognizes_uppercase_extension(self):
        type = models.File.type_from_name('foo.JPG')
        self.assertEquals(type, models.File.TYPE_IMAGE)

    def test_type_from_name_correctly_regognizes_lowercase_extension(self):
        type = models.File.type_from_name('foo.mp3')
        self.assertEquals(type, models.File.TYPE_AUDIO)

    def test_type_from_name_correctly_regognizes_mixedcase_extension(self):
        type = models.File.type_from_name('foo.JpEg')
        self.assertEquals(type, models.File.TYPE_IMAGE)

    def test_original_url_has_original_file_ext(self):
        f = models.File(title='foo', type=models.File.TYPE_VIDEO,
            orig_filename='foo.bar')
        f.save()
        self.assertEquals(f.original_url.rpartition('.')[2], 'bar')
        f.delete()

    def test_original_url_has_key_instead_of_original_name(self):
        f = models.File(title='foo', type=models.File.TYPE_VIDEO,
            orig_filename='foo.bar')
        f.save()
        key = f.original_url.rpartition('/')[2].partition('.')[0]
        self.assertEquals(key, '%s_%s' % (f.key, f.subkey_orig))
        f.delete()

    def test_ext_returns_extension_based_on_original_file_name(self):
        f = models.File(title='foo', type=models.File.TYPE_VIDEO,
            orig_filename='foo.bar')
        self.assertEquals(f.ext, 'bar')

    def test_update_replaces_old_segments(self):
        # TODO
        pass

    def test_all_files_have_to_exist(self):
        # TODO
        pass


class UtilsTest(ClientTestCase):
    """Tests utils from ``content.utils`` module.
    """

    def test_returned_string_is_exactly_twice_long_as_number_of_bytes(self):
        s = utils.get_rand_bytes_as_hex(5)
        self.assertEquals(len(s), 10)

        s = utils.get_rand_bytes_as_hex(200)
        self.assertEquals(len(s), 400)

    def test_returned_string_is_encoded_as_hex(self):
        s = utils.get_rand_bytes_as_hex(100)
        try:
            int(s, 16)
        except ValueError:
            self.fail('String %s contains digits out of hex range.' % (s,))

    def test_gen_file_key_returns_string(self):
        key = utils.gen_file_key()
        self.assertTrue(isinstance(key, str))


class ModuleDescriptionParserTest(ClientTestCase):
    """Tests parser of the module description.
    """

    fixtures = ('sample.json', 'test-course.json','test-users-content.json',)


    def _parse(self, descr):
        p = models.ModuleDescrParser(descr, User.objects.get(id=1))
        return p.parse()

    def test_non_json_messages_raises_exception(self):
        try:
            self._parse('foo bar')
            self.fail('Non JSON message accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, None)

    def test_version_field_is_required(self):
        try:
            self._parse('{ "meta": {}, "track0": [], "track1": [] }')
            self.fail('Module descr without the version field accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'version')

    def test_raises_error_on_unknown_version(self):
        try:
            self._parse('{ "version": -1 }')
            self.fail('Invalid version of module descr accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'version')

    def test_meta_field_is_required(self):
        try:
            self._parse('{ "version": 1, "track0": [], "track1": [] }')
            self.fail('Module descr without the meta field accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'meta')

    def test_track0_field_is_required(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track1": [ ]
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr without the track0 field accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0')

    def test_track1_field_is_required(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [ ]
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr without the track1 field accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track1')

    def test_start_field_is_required_for_each_item(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [
                {
                    "id": 1,
                    "start": 1,
                    "end": 1
                },
                {
                    "id": 2,
                    "end": 2
                }
            ],
            "track1": []
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr without the start field in one of entries accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0.1.start')

    def test_id_field_is_required_for_each_item(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [
                { "start": 1, "end": 1 },
                { "id": 2, "start": 2, "end": 2 }
            ],
            "track1": [
                { "id": 7, "start": 2, "end": 2 }
            ]
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr without the id field in one of entries accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0.0.id')

    def test_end_field_is_required_for_each_item(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [
                { "id": 1, "start": 1, "end": 1 },
                { "id": 2, "start": 2, "end": 2 }
            ],
            "track1": [
                { "id": 6, "start": 1, "playback_mode": "once"  },
                { "id": 7, "start": 2, "end": 2, "playback_mode": "once" }
            ]
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr without the end field in one of entries accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track1.0.end')

    def test_start_field_must_be_int(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [
                {
                    "id": 1,
                    "start": "1",
                    "end": 1
                }
            ],
            "track1": []
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr with invalid start field value accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0.0.start')

    def test_start_field_must_be_positive_int(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [
                {
                    "id": 1,
                    "start": -3,
                    "end": 1
                }
            ],
            "track1": []
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr with invalid start field value accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0.0.start')

    def test_the_title_field_is_required(self):
        m = """
        {
            "version": 1,
            "meta": { "objective": "objective of the module" },
            "track0": [ ],
            "track1": [ ]
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr without the title field accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'meta.title')

    def test_the_title_field_cannot_be_empty(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "", "objective": "objective of the module" },
            "track0": [ ],
            "track1": [ ]
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr with the empty title field accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'meta.title')

    def test_the_objective_field_is_required(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "sample title" },
            "track0": [ ],
            "track1": [ ]
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr without the objective field accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'meta.objective')

    def test_module_id_must_be_int_if_given(self):
        m = """
        {
            "version": 1,
            "meta": { "id": "asd", "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [],
            "track1": []
        }
        """

        try:
            self._parse(m)
            self.fail('Module with incorrect id accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'meta.id')

    def test_module_must_exist_if_id_is_given(self):
        m = """
        {
            "version": 1,
            "meta": { "id": 100, "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [],
            "track1": []
        }
        """
        try:
            self._parse(m)
            self.fail('Module descr for inexisting module accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'meta.id')

    def test_accepts_playback_mode_on_track1(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [],
            "track1": [
                {
                    "id": 2,
                    "start": 1,
                    "end": 1,
                    "playback_mode": "once"
                }
            ]
        }
        """
        try:
            self._parse(m)
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0.0.playback_mode')
            self.fail('Module descr with playback_mode set on an entry in track1 rejected.')

    def test_persists_owner(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [],
            "track1": [
                {
                    "id": 2,
                    "start": 1,
                    "end": 1,
                    "playback_mode": "once"
                }
            ]
        }
        """
        try:
            self.assertEquals(
                models.Course.objects.get(id=self._parse(m)).owner,
                User.objects.get(id=1))
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0.0.playback_mode')
            self.fail('Module descr with playback_mode set on an entry in track1 rejected.')

    def test_intersection_of_segments_files_groups_and_user_groups(self):
        m = """
        {
            "version": 1,
            "meta": { "id": 1, "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [
                {
                    "id": 26,
                    "start": 1,
                    "end": 1
                }
            ],
            "track1": [
                {
                    "id": 27,
                    "start": 1,
                    "end": 1,
                    "playback_mode": "once"
                }
            ]
        }
        """
        try:
            self.assertEquals(models.Course.objects.get(id=self._parse(m)).groups_can_be_assigned_to.all().count(), 1)
        except models.ModuleDescrError, e:
            print e.reason
            self.assertEquals(e.field, 'track0.0.playback_mode')
            self.fail('Module descr with playback_mode set on an entry in track1 rejected.')

    def test_rejects_playback_mode_on_track0(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [
                {
                    "id": 1,
                    "start": 1,
                    "end": 1,
                    "playback_mode": "once"
                }
            ],
            "track1": []
        }
        """
        try:
            self._parse(m)
            self.fail('Module descr with playback_mode set on an entry in track0 accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0.0.playback_mode')

    def test_rejects_incorrect_playback_mode(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [],
            "track1": [
                {
                    "id": 1,
                    "start": 1,
                    "end": 1,
                    "playback_mode": "thisisinvalid"
                }
            ]
        }
        """
        try:
            self._parse(m)
            self.fail('Module descr with invalid playback_mode accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track1.0.playback_mode')

    def test_playback_mode_once_is_ok(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [],
            "track1": [
                {
                    "id": 1,
                    "start": 1,
                    "end": 1,
                    "playback_mode": "once"
                }
            ]
        }
        """
        try:
            self._parse(m)
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track1.0.playback_mode')
            self.fail('Module descr with a playback_mode "once" rejected.')

    def test_playback_mode_repeat_is_ok(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [],
            "track1": [
                {
                    "id": 1,
                    "start": 1,
                    "end": 1,
                    "playback_mode": "repeat"
                }
            ]
        }
        """
        try:
            self._parse(m)
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track1.0.playback_mode')
            self.fail('Module descr with a playback_mode "repeat" rejected.')

    def test_start_cannot_be_after_end(self):
        m = """
        {
            "version": 1,
            "meta": { "title": "foobar", "objective": "", "allow_download": true, "allow_skipping": true },
            "track0": [
                {
                    "id": 1,
                    "start": 2,
                    "end": 1
                }
            ],
            "track1": []
        }
        """

        try:
            self._parse(m)
            self.fail('Module descr with start after end accepted.')
        except models.ModuleDescrError, e:
            self.assertEquals(e.field, 'track0.0.end')


class FakeStorage(object):
    """Limited Django storage backend.
    """

    def __init__(self):
        self.last_filename = None
        self.last_buf = None

    def open(self, path, mode):
        self.last_filename = path.rpartition('/')[2]
        self.last_buf = FakeFile()
        return self.last_buf

    def path(self, path):
        return "path"


class FakeFile(object):
    """Fake file returned from the storage backend.
    """

    def __init__(self):
        self.size = 0
        self.closed = False

    def write(self, s):
        self.size += len(s)

    def close(self):
        self.closed = True


class ModulesListTest(ClientTestCase):
    fixtures = ('sample.json', 'test-course.json', 'test-users-content.json',)
    url = '/content/modules/list/'

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def _get_modules(self, url='/content/modules/list/'):
        c = self._get_client_admin()
        response = c.get(url)
        return json.loads(response.content)

    def test_default_response_is_json(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        try:
            return json.loads(response.content)
        except ValueError, e:
            self.fail('Error parsing default json response from url: '+self.url)

    def test_get_return_modules_number_for_admin(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        modules = json.loads(response.content)
        #drafts
        self.assertEquals(modules[0]['meta']['id'], 2)
        self.assertEquals(modules[1]['meta']['id'], 1)

        self.assertEquals(len(modules), 2)

    def test_get_return_modules_number_for_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url)
        modules = json.loads(response.content)
        #drafts
        self.assertEquals(modules[0]['meta']['id'], 2)
        self.assertEquals(modules[1]['meta']['id'], 1)
        #assigned
        self.assertEquals(modules[2]['meta']['id'], 3)
        self.assertEquals(modules[3]['meta']['id'], 4)
        self.assertEquals(modules[4]['meta']['id'], 5)
        #inactive
        self.assertEquals(modules[5]['meta']['id'], 6)
        self.assertEquals(modules[6]['meta']['id'], 300)

        self.assertEquals(len(modules), 7)

    def test_module_has_meta(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        modules = json.loads(response.content)
        module = modules[0]
        self.assertTrue('meta' in module)

    def test_module_has_objectives(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        modules = json.loads(response.content)
        meta = modules[0]['meta']
        self.assertTrue('objective' in meta)

    def test_module_has_title(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        modules = json.loads(response.content)
        meta = modules[0]['meta']
        self.assertTrue('title' in meta)

class ActiveModulesListTest(ClientTestCase):
    fixtures = ('sample.json', 'test-course.json', 'test-users-content.json',)
    url = '/content/modules/active/list/'

    def test_get_return_modules_number_for_admin(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        modules = json.loads(response.content)
        self.assertEquals(1, len(modules))

    def test_get_return_modules_number_for_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url)
        modules = json.loads(response.content)
        self.assertEquals(3, len(modules))
        self.assertEquals(modules[0]['meta']['id'], 3)
        self.assertEquals(modules[1]['meta']['id'], 4)
        self.assertEquals(modules[2]['meta']['id'], 5)
        
class SaveManageContentTest(ClientTestCase):
    fixtures = ('sample.json', 'test-course.json', 'test-tags.json', 'test-users-content.json',)
    url = "/content/manage/save/"

    def test_does_not_accept_user(self):
        c = self._get_client_user()
        response = c.post(self.url)
        self.assertEquals(response.status_code, 302)

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.post(self.url)
        self.assertNotEquals(response.status_code, 302)

    def test_accepts_admin(self):
        c = self._get_client_admin()
        response = c.post(self.url)
        self.assertNotEquals(response.status_code, 302)

    def test_does_not_accept_get_request(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 405)

    def test(self):
        c = self._get_client_admin()
        response = c.post(self.url,
                          json.dumps({'file_id': '1',
                                      "title": "title",
                                      "note": "note",
                                      "language": "10",
                                      "expires_on": "2010-12-12",
                                      "delete_after_expire": True,
                                      "new_tags_names": [],
                                      "duration": 1,
                                      "owner": 2,
                                      "selected_groups_ids": [1, 2],
                                      "is_downloadable": False,
                                      "tags_ids": [101]}),
                          content_type='application/json')
        self.assertEquals(json.loads(response.content)["status"], "OK")
        file = models.File.objects.get(id=1, tag=101)
        self.assertEquals(file.title, "title")
        self.assertEquals(file.note, "note")
        self.assertTrue(file.delete_expired)
        self.assertFalse(file.is_downloadable)
        self.assertEquals(file.duration, 1)
        self.assertEquals(file.groups.all().count(), 2)
        self.assertEquals(file.owner.id, 2)
        self.assertEquals(file.tag_set.all().count(), 4)

    def test_should_handle_optional_fields(self):
        c = self._get_client_admin()
        response = c.post(self.url,
                          json.dumps({'file_id': '1',
                                      "title": "title",
                                      "note": "",
                                      "expires_on": "",
                                      "language": "en",
                                      "new_tags_names": [],
                                      "owner": 2,
                                      'duration': 3,
                                      "selected_groups_ids": [1, 2],
                                      "is_downloadable": False,
                                      "delete_after_expire": True,
                                      "tags_ids": [101]}),
                          content_type='application/json')
        self.assertEquals(json.loads(response.content)["status"], "OK")
        file = models.File.objects.get(id=1, tag=101)
        self.assertEquals(file.title, "title")
        self.assertFalse(file.expires_on)
        self.assertEquals(file.note, "")
        self.assertEquals(file.language, "en")
        self.assertTrue(file.delete_expired)
        self.assertFalse(file.is_downloadable)


    def test_should_save_video_without_asking_for_duration(self):
        c = self._get_client_admin()
        response = c.post(self.url,
                          json.dumps({'file_id': '15',
                                      "title": "title",
                                      "note": "",
                                      "expires_on": "",
                                      "language": "en",
                                      "new_tags_names": [],
                                      "owner": 2,
                                      "selected_groups_ids": [1, 2],
                                      "is_downloadable": False,
                                      "delete_after_expire": True,
                                      "tags_ids": [101]}),
                          content_type='application/json')
        self.assertEquals(json.loads(response.content)["status"], "OK")
        file = models.File.objects.get(id=15, tag=101)
        self.assertEquals(file.title, "title")
        self.assertFalse(file.expires_on)
        self.assertEquals(file.note, "")
        self.assertEquals(file.language, "en")
        self.assertTrue(file.delete_expired)
        self.assertFalse(file.is_downloadable)

    def test_should_set_default_file_owner(self):
        c = self._get_client_admin()
        response = c.post(self.url,
                          json.dumps({'file_id': '1',
                                      "title": "title",
                                      "note": "note",
                                      "language": "10",
                                      "expires_on": "2010-12-12",
                                      "delete_after_expire": True,
                                      "new_tags_names": [],
                                      "owner": '',
                                      "duration": 3,
                                      "selected_groups_ids": [1, 2],
                                      "is_downloadable": False,
                                      "tags_ids": [101]}),
                          content_type='application/json')
        self.assertEquals(json.loads(response.content)["status"], "OK")
        file = models.File.objects.get(id=1)
        self.assertEquals(file.owner.id, 1)


class EditContentTest(ClientTestCase):
    fixtures = ('sample.json', 'test-course.json', 'test-tags.json', 'test-users-content.json',)
    url = "/content/manage/%d/"

    def test_does_not_accept_not_logged_user(self):
        c = client.Client()
        response = c.get(self.url % 1)
        self.assertEquals(response.status_code, 302)

    def test_accepts_get_requests(self):
        c = self._get_client_superadmin()
        response = c.get(self.url % 1)
        self.assertEquals(response.status_code, 200)

    def test_does_not_accept_post_requests(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 405)

    def test_should_use_correct_template(self):
        c = self._get_client_superadmin()
        response = c.get(self.url % 1)
        self.assertTemplateUsed(response, 'content/module_content.html')

    def test_accepts_superadmin(self):
        c = self._get_client_superadmin()
        response = c.get(self.url % 1)
        self.assertEquals(response.status_code, 200)

    def test_accepts_owner(self):
        c = self._get_client_admin()
        response = c.get(self.url % 1)
        self.assertEquals(response.status_code, 200)

    def test_does_not_accept_non_owner_non_superadmin(self):
        c = self._get_client_user()
        response = c.get(self.url % 1)
        self.assertEquals(response.status_code, 400)


class DeleteExpiredTaskTest(ClientTestCase):
    fixtures = ('sample.json', 'test-course.json', 'test-tags.json',)

    def test_task_marks_deleted_content(self):
        files_count = models.File.objects.filter(expires_on__isnull = False,
                                                expires_on__lt = datetime.date.today(),
                                                is_removed = False).count()

        tasks.delete_expired_content()

        files_count_new = models.File.objects.filter(expires_on__isnull = False,
                                                     expires_on__lt = datetime.date.today(),
                                                     is_removed = False).count()

        self.assertTrue(files_count != files_count_new)
        self.assertEquals(files_count_new, 0)


    def test_task_deactivates_modules(self):
        active_modules = models.Course.objects.filter(segment__file__expires_on__lt = datetime.date.today(),
                                                      segment__file__is_removed = True,
                                                      active=True).count()
        self.assertEquals(active_modules, 0)


class FakeTrackingService(object):
    def segmentIsLearnt(self, user_id, segment_id):
        return False

class SerializersTest(ClientTestCase):
    """Tests for the content.serializers module.
    """
    fixtures = ('test-users-content.json',)

    def test_serialize_course_handles(self):
        owner = auth_models.User.objects.get(id=1)
        course = models.Course(title='Test Course', objective='Test!', language="10", owner=owner, allow_download=True)
        course.save()

        for i in range(1, 40):
            group = auth_models.Group(name=str(i))
            group.save()
            models.CourseGroup(course=course, group=group,
                       assigner=owner,
                       assigned_on=datetime.datetime.now()).save()

        file = models.File(
            orig_filename='foo.jpg',
            type=models.File.TYPE_IMAGE,
	    status=models.File.STATUS_AVAILABLE,
            is_downloadable=True)
        file.save()
        segment = models.Segment(
            course=course,
            file=file,
            track=0,
            start=0,
            end=0)
        segment.save()

        user = auth_models.User()
        user.save()

        data = serializers.serialize_course(course, user, FakeTrackingService())

        self.assertTrue(data['track0'][0]['expires_on'] is None)
        self.assertTrue(data['track0'][0]['allow_downloading'] is True)
        self.assertEquals(data['meta']['objective'], "Test!")
        self.assertEquals(data['meta']['language'], "10")
        self.assertEquals(data['meta']['language_name'], "Unspecified")
        self.assertEquals(data['meta']['ownerId'], owner.id)
        self.assertEquals(data['meta']['ownerName'], str(owner))
        self.assertTrue(data['meta']['created_on'])
        self.assertEquals(data['meta']['state'], "DRAFT")
        self.assertEquals(data['meta']['state_code'], Draft.CODE)
        self.assertEquals(len(data['meta']['groups_names']), 39)
        self.assertEquals(len(json.loads(data['meta']['available_actions'])), 2)

    def test_links_to_scorm_files_for_users_specify_real_segment_id(self):
        course = models.Course(title='Test Course', objective='Test!')
        course.save()
        file = models.File(
            orig_filename='foo.zip',
            type=models.File.TYPE_SCORM)
        file.save()
        segment = models.Segment(
            course=course,
            file=file,
            track=0,
            start=0,
            end=0)
        segment.save()

        user = auth_models.User()
        user.save()
        profile = mgmnt_models.UserProfile(user=user, role=mgmnt_models.UserProfile.ROLE_USER)
        profile.save()

        url = urlparse.urlsplit(segment.get_view_url(user))
        qs = urlparse.parse_qs(url.query)
        self.assertEquals(qs['segmentID'][0], str(segment.id))

    def test_links_to_scorm_files_for_admins_specify_preview_segment_id(self):
        course = models.Course(title='Test Course', objective='Test!')
        course.save()
        file = models.File(
            orig_filename='foo.zip',
            type=models.File.TYPE_SCORM)
        file.save()
        segment = models.Segment(
            course=course,
            file=file,
            track=0,
            start=0,
            end=0)
        segment.save()

        user = auth_models.User()
        user.save()
        profile = mgmnt_models.UserProfile(user=user, role=mgmnt_models.UserProfile.ROLE_ADMIN)
        profile.save()

        url = urlparse.urlsplit(segment.get_view_url(user))
        qs = urlparse.parse_qs(url.query)
        self.assertEquals(qs['segmentID'][0], 'preview')

    def test_propery_formats_key_to_scorm_files_for_users(self):
        """Serializer properly formats URL for scorm files.

        Due to a bad use of ``urllib.urlencode`` query string was improperly
        formatted.
        """

        course = models.Course(title='Test Course', objective='Test!')
        course.save()
        f = models.File(
            orig_filename='foo.zip',
            type=models.File.TYPE_SCORM)
        f.save()
        s = models.Segment(course=course, file=f, track=0, start=0, end=0)
        s.save()

        user = auth_models.User()
        user.save()
        profile = mgmnt_models.UserProfile(user=user, role=mgmnt_models.UserProfile.ROLE_USER)
        profile.save()

        url = urlparse.urlsplit(s.get_view_url(user))
        qs = urlparse.parse_qs(url.query)
        self.assertEquals(f.key, qs['scormPackageID'][0])

    def test_json_format_has_duration_for_pdf_files(self):
        course, file, user = self._create_course('foo.pdf', models.File.TYPE_PDF)
        file.duration = 3
        file.save()

        data = serializers.serialize_course(course, user, FakeTrackingService())

        self.assertEquals(data['track0'][0]['duration'], 3)

    def test_xml_format_has_duration_for_pdf_files(self):
        course, file, user = self._create_course('foo.pdf', models.File.TYPE_PDF)
        file.duration = 3
        file.save()

        data = serializers.serialize_course_xml(course, user)

        tree = ET.fromstring(data)
        entry = tree.find('track/entry')
        self.assertEquals(entry.attrib.get('duration'), str(3))

    def _create_course(self, file_name, file_type):
        user = auth_models.User()
        user.save()

        course = models.Course(title='Test Course', objective='Test!', owner=user)
        course.save()

        file = models.File(orig_filename=file_name, type=file_type)
        file.save()

        segment = models.Segment(
            course=course, file=file, track=0, start=0, end=0)
        segment.save()

        return course, file, user


class ExceptionalConverter(convert.BaseConverter):
    class Exc(Exception):
        pass

    class File(object):
        status = None
        def save(self):
            pass

    def __init__(self, exc_in_initialize=True):
        self._file = self.File()
        self.exc_in_initialize = exc_in_initialize
        self.was_finalized = False

    def _initialize(self):
        if self.exc_in_initialize:
            raise self.Exc()

    def _convert(self):
        raise self.Exc()

    def _finalize(self):
        self.was_finalized = True


class FakeLogger(object):
    def __init__(self):
        self.logs = []

    def info(self, msg):
        self.logs.append(msg)

    def error(self, msg):
        self.logs.append(msg)


class FailingConverter(convert.BaseConverter):
    def _get_command(self):
        raise convert.ConversionError('Conversion has failed on purpose!')

class SuccessfulConverter(convert.BaseConverter):
    def _convert(self):
        pass

    def _create_thumbnail(self):
        pass


class ConvertTest(TestCase):
    fake_type = 31337

    def test_run_command_raises_exception_on_error(self):
        conv = convert.BaseConverter(None, None, None)
        self.assertRaises(utils.CommandError, conv._run_command, ['false'])

    def test_finalize_gets_called_on_exception_in_initialize(self):
        conv = ExceptionalConverter()
        try:
            conv.convert()
        except convert.ConversionError:
            pass

        self.assertTrue(conv.was_finalized)

    def test_no_converters_are_registered_with_our_unique_test_only_type(self):
        try:
            self.assertEquals(None, convert.register(self.fake_type, None))
        finally:
            convert.unregister(self.fake_type)

    def test_unregister_removes_converter(self):
        try:
            conv = object()
            convert.register(self.fake_type, conv)
            convert.unregister(self.fake_type)
            self.assertEquals(None, convert.register(self.fake_type, None))
        finally:
            convert.unregister(self.fake_type)

    def test_finalize_gets_called_on_exception_in_convert(self):
        conv = ExceptionalConverter(exc_in_initialize=False)
        try:
            conv.convert()
        except convert.ConversionError:
            pass

        self.assertTrue(conv.was_finalized)

    def test_register_returns_previous_converter(self):
        try:
            converter = object()
            # just to make sure we don't register converter for this magic number
            self.assertEquals(None, convert.register(self.fake_type, converter))

            self.assertEquals(converter, convert.register(self.fake_type, None))
        finally:
            convert.unregister(self.fake_type)

    def test_get_converter_for_unknown_type_raises_error(self):
        fake_file = FakeFile()
        fake_file.type = self.fake_type

        self.assertRaises(
            convert.ConversionError,
            convert.get_converter, fake_file, None, None)

    def test_failed_conversion_marks_file_as_invalid(self):
        file = self._create_file('foo.jpeg', models.File.TYPE_IMAGE)
        conv = FailingConverter(file, None, FakeLogger())
        self.assertRaises(
            convert.ConversionError,
            conv.convert)
        self.assertEquals(file.status, models.File.STATUS_INVALID)

    def test_successful_conversion_marks_file_as_available(self):
        file = self._create_file('foo.jpeg', models.File.TYPE_IMAGE)
        conv = SuccessfulConverter(file, None, FakeLogger())
        conv.convert()
        self.assertEquals(file.status, models.File.STATUS_AVAILABLE)

    def test_pdf_files_are_converted_using_mocked_command(self):
        file = self._create_file('foo.pdf', models.File.TYPE_PDF)

        from django.core.files import storage
        conv = convert.PDFConverter(file, storage.default_storage, FakeLogger())
        conv._convert_preview = lambda: None
        conv._convert_thumbnail = lambda: None
        conv.convert()
        self.assertEquals(file.status, models.File.STATUS_AVAILABLE)

    def test_can_recognize_errors_in_pdf_converter(self):
        file = self._create_file('foo.pdf', models.File.TYPE_PDF)
        # FAIL is a magic flag for mocked converter which causes it to fail
        # like the original converter (pdftohtml).
        file.subkey_orig = file.subkey_orig[-4] + 'FAIL'
        file.save()
        conv = convert.PDFConverter(file, storage.default_storage, FakeLogger())
        self.assertRaises(convert.ConversionError, conv.convert)
        self.assertEquals(file.status, models.File.STATUS_INVALID)

    def _create_file(self, name, type):
        file = models.File(orig_filename=name, type=type)
        file.save()
        return file

class VideoConverterTest(TestCase):

    fixtures = ('test-files.json',)

    def setUp(self):
        self.vc = VideoConverter(File.objects.get(id=1), FakeStorage(), None)
        self.vc._tmp = ["tmp.mp4", "tmp.webm", "tmp.ogv", "temp.flv"]

    def test_should_be_medium_if_there_is_no_config_entry(self):
        self.assertEquals(self.vc._get_command_medium_quality(), self.vc._get_command_flv())

    def test_should_return_same_command_for_high_quality(self):
        ConfigEntry(config_key=ConfigEntry.CONTENT_QUALITY_OF_CONTENT, config_val=ConfigEntry.QUALITY_TYPE_HIGH).save()
        self.assertEquals(self.vc._get_command_high_quality(), self.vc._get_command_flv())

    def test_should_return_same_command_for_medium_quality(self):
        ConfigEntry(config_key=ConfigEntry.CONTENT_QUALITY_OF_CONTENT, config_val=ConfigEntry.QUALITY_TYPE_MEDIUM).save()
        self.assertEquals(self.vc._get_command_medium_quality(), self.vc._get_command_flv())

    def test_should_return_same_command_for_low_quality(self):
        ConfigEntry(config_key=ConfigEntry.CONTENT_QUALITY_OF_CONTENT, config_val=ConfigEntry.QUALITY_TYPE_LOW).save()
        self.assertEquals(self.vc._get_command_low_quality(), self.vc._get_command_flv())

class CourseStateMachineryTest(ClientTestCase):
    fixtures = ('test-course.json', 'test-users-content.json',)

    def test_default_state_should_be_draft(self):
        self.assertEquals(self.course().get_state().code(), Draft.CODE)

    def test_segments_required_for_activation(self):
        course = self.course(3)
        course.state_code = Draft.CODE
        course.save()
        errors = course.get_state().act("activate")

        self.assertEquals("At least one segment is required.", errors[0])

    def test_objectives_required_for_activation(self):
        course = self.course(2)
        course.objective = ""
        course.save()
        errors = course.get_state().act("activate")
        self.assertFalse(errors)

    def test_at_least_one_groups_can_assigned_to_required_for_activation(self):
        course = self.course(2)
        course.groups_can_be_assigned_to.clear()
        course.save()
        errors = course.get_state().act("activate")
        self.assertEquals("""Module must have at least one group in "Can be assigned to" section.""", errors[0])

    def test_segments_required_for_reactivation(self):
        course = self.course(3)
        course.state_code = Deactivated.CODE
        course.save()
        errors = course.get_state().act("reactivate")

        self.assertEquals("At least one segment is required.", errors[0])

    def test_objectives_required_for_reactivation(self):
        course = self.course(2)
        course.state_code = Deactivated.CODE
        course.objective = ""
        course.save()
        errors = course.get_state().act("reactivate")
        self.assertFalse(errors)

    def test_at_least_one_groups_can_assigned_to_required_for_reactivation(self):
        course = self.course(2)
        course.groups_can_be_assigned_to.clear()
        course.state_code = Deactivated.CODE
        course.save()
        errors = course.get_state().act("reactivate")
        self.assertEquals("""Module must have at least one group in "Can be assigned to" section.""", errors[0])

    def test_segments_required_for_reactivation_used(self):
        course = self.course(3)
        course.state_code = DeactivatedUsed.CODE
        course.save()
        errors = course.get_state().act("reactivate")

        self.assertEquals("At least one segment is required.", errors[0])

    def test_objectives_required_for_reactivation_used(self):
        course = self.course(2)
        course.state_code = DeactivatedUsed.CODE
        course.objective = ""
        course.save()
        errors = course.get_state().act("reactivate")
        self.assertFalse(errors)

    def test_at_least_one_groups_can_assigned_to_required_for_reactivation_used(self):
        course = self.course(2)
        course.groups_can_be_assigned_to.clear()
        course.state_code = DeactivatedUsed.CODE
        course.save()
        errors = course.get_state().act("reactivate")
        self.assertEquals("""Module must have at least one group in "Can be assigned to" section.""", errors[0])

    def test_activated_code(self):
        errors = self.course().get_state().act("activate")

        self.assertFalse(errors, errors)
        self.assertEquals(self.course().get_state().code(), 2)
        self.assertTrue(self.course().published_on)

    def test_deactivated_state_code(self):
        course = self.course()
        course.state_code = ActiveAssign.CODE
        course.save()
        errors = self.course().get_state().act("deactivate")

        self.assertFalse(errors, errors)
        self.assertEquals(self.course().get_state().code(), Deactivated.CODE)
        self.assertTrue(self.course().deactivated_on)

    def test_should_not_fill_deactivated_on_date(self):
        course = self.course()
        course.state_code = ActiveAssign.CODE
        course.save()
        errors = self.course().get_state().act("remove_assignments")

        self.assertFalse(errors, errors)
        self.assertEquals(self.course().get_state().code(), Active.CODE)
        self.assertFalse(self.course().deactivated_on)

    def test_deactivated_state_code(self):
        course = self.course()
        course.state_code = ActiveInUse.CODE
        course.save()
        errors = self.course().get_state().act("deactivate")

        self.assertFalse(errors, errors)
        self.assertEquals(self.course().get_state().code(), DeactivatedUsed.CODE)
        self.assertTrue(self.course().deactivated_on)

    def test_non_expired_segments_required_for_activation(self):
        File.objects.filter(id=1).update(status=File.STATUS_EXPIRED)
        errors = self.course().get_state().act("activate")
        self.assertEquals("""Segment "Praesent pharetra turpis ac turpis pharetra." is expired.""", errors[0])

    def test_expires_on_must_be_at_least_week_forward_for_activation_error(self):
        course = self.course(2)
        course.expires_on = (datetime.datetime.now() + datetime.timedelta(days=6)).date()
        course.save()
        errors = course.get_state().act("activate")
        self.assertEquals("'Expires to' date must be at least 1 week forward.", errors[0])

    def test_expires_on_must_be_at_least_week_forward_for_activation(self):
        course = self.course(2)
        course.expires_on = (datetime.datetime.now() + datetime.timedelta(days=7)).date()
        course.save()
        errors = course.get_state().act("activate")
        self.assertFalse(errors, errors)
        self.assertEquals(course.get_state().code(), 2)
        
    def test_available_actions_in_states(self):
        # draft
        self.validate_actions("activate", "delete")

        # active
        self._act_and_validate_errors("activate")
        self.validate_actions("assign", "delete", "expire", "back_to_draft")

        # active assign
        self._act_and_validate_errors("assign")
        self.validate_actions("remove_assignments", "deactivate", "expire", "delete", "work_done")

        # deactivated
        self._act_and_validate_errors("expire")
        self.validate_actions("delete", "reactivate")

        # active assign
        self._act_and_validate_errors("reactivate")
        self.validate_actions("remove_assignments", "deactivate", "expire", "delete", "work_done")

        # active in use
        self._act_and_validate_errors("work_done")
        self.validate_actions("remove_user", "expire", "deactivate")

        # deactivated in use
        self._act_and_validate_errors("expire")
        self.validate_actions("remove", "remove_user", "reactivate")

        # removed
        self._act_and_validate_errors("remove")
        self.validate_actions()

    def _act_and_validate_errors(self, action_name):
        errors = self.course().get_state().act(action_name)
        self.assertFalse(errors, errors)

    def test_delete_action(self):
        self.course().get_state().act("delete")
        self.assertRaises(models.Course.DoesNotExist, self.course)

    def validate_actions(self, *args):
        for arg in args:
            self.assertTrue(arg in self.course().get_valid_actions())
        self.assertEquals(set(self.course().get_valid_actions()), set(args))

    def course(self, id=1):
       return models.Course.objects.get(id=id)


class ListCollectionsTest(ClientTestCase):
    fixtures = ('sample.json','test-users-content.json','test-collections.json')
    url = "/content/collections/"

    def test_does_not_accept_not_logged_user(self):
        c = client.Client()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_accepts_get_requests(self):
        c = self._get_client_superadmin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_does_not_accept_post(self):
        c = self._get_client_superadmin()
        response = c.post(self.url, {})
        self.assertEquals(response.status_code, 405)

    def test_get_returns_json(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        data = json.loads(response.content)

    def test_returned_json_contains_collections(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        data = json.loads(response.content)
        self.assertTrue(len(data) > 0)

    def test_returns_all_collections_of_user(self):
        c = self._get_client_admin()
        response = c.get(self.url)
        data = json.loads(response.content)
        self.assertEquals(len(data), 3)

class CreateCollectionTest(ClientTestCase):
    fixtures = ('sample.json','test-users-content.json')
    url = "/content/collections/save/"

    def test_does_not_accept_not_logged_user(self):
        c = client.Client()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 405)

    def test_does_not_accept_get(self):
        c = self._get_client_superadmin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 405)

    def test_accepts_post_requests(self):
        c = self._get_client_superadmin()
        response = c.post(self.url,
                          json.dumps({'meta': {'title':'new_collection_name'},
                                     'track0':[]}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 200)

    def test_creates_collection(self):
        c = self._get_client_superadmin()
        collections_num_old = models.Collection.objects.filter(owner__id=2).count()
        response = c.post(self.url,
                          json.dumps({'meta': {'title':'new_collection_name'},
                                     'track0':[]}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 200)
        collections_num_new = models.Collection.objects.filter(owner__id=2).count()
        self.assertEquals(collections_num_new, collections_num_old+1)

    def test_returns_json_with_id(self):
        c = self._get_client_superadmin()
        response = c.post(self.url,
                          json.dumps({'meta': {'title':'new_collection_name'},
                                     'track0':[]}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('id' in data)

class SaveCollectionTest(ClientTestCase):
    fixtures = ('sample.json','test-users-content.json', 'test-collections.json')
    url = "/content/collections/save/%d/"

    def test_does_not_accept_not_logged_user(self):
        c = client.Client()
        response = c.get(self.url%1)
        self.assertEquals(response.status_code, 405)

    def test_does_not_accept_get(self):
        c = self._get_client_superadmin()
        response = c.get(self.url%1)
        self.assertEquals(response.status_code, 405)

    def test_only_owner_accepted(self):
        c = self._get_client_admin()
        response = c.post(self.url%4,
                          json.dumps({'meta': {'title':'new_collection_name'},
                                     'track0':[]}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 400)

    def test_accepts_post_requests(self):
        c = self._get_client_superadmin()
        response = c.post(self.url%1,
                          json.dumps({'meta': {'title':'new_collection_name'},
                                     'track0':[]}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 200)

    def test_changes_collection_name_and_content(self):
        c = self._get_client_superadmin()
        elements_num_old = models.CollectionElem.objects.filter(collection__id=1).count()
        collection = models.Collection.objects.get(pk=1)
        self.assertTrue(elements_num_old != 3)
        self.assertTrue(collection.name != 'new_collection_name')
        response = c.post(self.url%1,
                          json.dumps({'meta': {'title':'new_collection_name'},
                                       'track0':[1, 2, 3]}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 200)
        elements_num_new = models.CollectionElem.objects.filter(collection__id=1).count()
        collection = models.Collection.objects.get(pk=1)
        self.assertEquals(elements_num_new, 3)
        self.assertEquals(collection.name, 'new_collection_name')

class DeleteCollectionTest(ClientTestCase):
    fixtures = ('sample.json','test-users-content.json', 'test-collections.json')
    url = "/content/collections/delete/%d/"

    def test_does_not_accept_not_logged_user(self):
        c = client.Client()
        response = c.get(self.url%4)
        self.assertEquals(response.status_code, 405)

    def test_does_not_accept_get(self):
        c = self._get_client_admin()
        response = c.get(self.url%4)
        self.assertEquals(response.status_code, 405)

    def test_only_owner_accepted(self):
        c = self._get_client_admin()
        response = c.post(self.url%4)
        self.assertEquals(response.status_code, 400)

    def test_deletes_given_collection(self):
        c = self._get_client_admin()
        collections_num_old = models.Collection.objects.filter(owner__id=1).count()
        response = c.post(self.url%1)
        self.assertEquals(response.status_code, 200)
        collections_num_new = models.Collection.objects.filter(owner__id=1).count()
        self.assertEquals(collections_num_old, collections_num_new+1)

    def test_deleting_nonexisting_collection_gives_404(self):
        c = self._get_client_admin()
        response = c.post(self.url%100000)
        self.assertEquals(response.status_code, 404)

class ChangeStateTest(ClientTestCase):
    fixtures = ('test-course.json', 'test-users-content.json',)
    url = "/content/modules/%d/state/"

    def test(self):
        c = self._get_client_admin()
        response = c.post(self.url % 1, json.dumps({'new_state': 'activate'}), content_type='application/json')
        data = json.loads(response.content)
        self.assertEquals("OK", data['status'])

class DeleteContentFile(ClientTestCase):
    fixtures = ('sample.json', 'test-users-content.json', 'test-course.json')
    url = "/content/manage/%d/delete/"

    def _custom_remove(self, file):
        self.removed_files.append(file)

    def setUp(self):
        self.removed_files = []
        os.remove = self._custom_remove
        self.orig_isfile = os.path.isfile
        os.path.isfile = lambda file: True

    def tearDown(self):
        os.path.isfile = self.orig_isfile

    def test_admin_cant_remove_not_his_file(self):
        response = self._get_client_admin().post(self.url % 2)
        self.assertEquals(400, response.status_code)
        self.assertEquals("Admin can remove only his files.", response.content)
        
    def test_admin_cant_remove_files_from_active_courses(self):
        response = self._get_client_admin().post(self.url % 9)
        self.assertEquals(400, response.status_code)
        self.assertEquals("Admin cant remove files which are in use by active courses.", response.content)

    def test_superadmin_should_remove_only_file_from_disk_if_file_is_used(self):
        response = self._get_client_superadmin().post(self.url % 9)
        self.assertEquals(200, response.status_code)
        file = File.objects.get(id=9)
        self.assertEquals(file.status, File.STATUS_REMOVED)
        self.assertTrue(os.path.join(settings.MEDIA_ROOT, settings.CONTENT_AVAILABLE_DIR, file.conv_file_path) in self.removed_files)
        self.assertTrue(os.path.join(settings.MEDIA_ROOT, settings.CONTENT_UPLOADED_DIR, file.orig_file_path) in self.removed_files)
        self.assertTrue(os.path.join(settings.MEDIA_ROOT, settings.CONTENT_THUMBNAILS_DIR, file.thumbnail_file_path) in self.removed_files)

    def test_superadmin_can_remove_not_his_file(self):
        response = self._get_client_superadmin().post(self.url % 4)
        self.assertEquals(200, response.status_code)

    def test_should_invoke_remove_on_existing_files(self):
        file = File.objects.get(id=4)
        c = self._get_client_superadmin()
        response = c.post(self.url % 4)
        self.assertEquals(200, response.status_code)
        self.assertRaises(Http404, get_object_or_404, File, id=4)
        self.assertTrue(os.path.join(settings.MEDIA_ROOT, settings.CONTENT_AVAILABLE_DIR, file.conv_file_path) in self.removed_files)
        self.assertTrue(os.path.join(settings.MEDIA_ROOT, settings.CONTENT_UPLOADED_DIR, file.orig_file_path) in self.removed_files)
        self.assertTrue(os.path.join(settings.MEDIA_ROOT, settings.CONTENT_THUMBNAILS_DIR, file.thumbnail_file_path) in self.removed_files)

class ChooseFileFromDmsTest(ClientTestCase):
    fixtures = ('test-users-content.json',)
    url = "/content/dms/"

    def test_valid_template_is_used(self):
        response = self._get_client_admin().get(self.url)
        self.assertTemplateUsed(response, 'content/dialogs/choose_file_from_dms.html')

class DmsFiles(ClientTestCase):
    fixtures = ('test-users-content.json',)
    url = "/content/dms/files/"

    def test_dms_disabled(self):
        ConfigEntry(config_val=False, config_key=ConfigEntry.CONTENT_USE_DMS).save()
        response = self._get_client_admin().get(self.url)
        self.assertEquals(response.status_code, 400)



# vim: set et sw=4 ts=4 sts=4 tw=78:
