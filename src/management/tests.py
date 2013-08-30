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

import json, StringIO

from datetime import date
from django.core import mail
from django import http
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import User
from django.test import client, TestCase, TransactionTestCase
from django.shortcuts import get_object_or_404
from content.course_states import ActiveAssign, DeactivatedUsed, Deactivated
from content.models import Course

from management import forms, models
from management.models import OneClickLinkToken
from plato_common.test_utils import ClientTestCase


def create_user(username='newuser', role=models.UserProfile.ROLE_USER):
    user = auth_models.User.objects.create_user(
        username=username,
        email='%s@example.net' % (username,),
        password=None,
        )
    user.first_name = "John"
    user.last_name = "Doe"
    user.save()

    profile = models.UserProfile(
        user=user,
        role=role
        )
    profile.save()

    return user

def create_user_over_http(url, client, **data):
    default = {
        'group': 1,
        'username': 'username',
        'email': 'test@test.com',
        'first_name': 'first name',
        'language': 'fr',
        'last_name': 'last name',
        'role': models.UserProfile.ROLE_USER,
        }
    default.update(**data)

    # Remove default field if it's value in data is None.
    for field, value in data.iteritems():
        if value is None and field in default:
            del default[field]

    return client.post(url, default)

class CreateGroupTest(ClientTestCase):
    fixtures = ('test-users-management.json',)

    url = '/management/groups/create/'

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def test_get_request_returns_form(self):
        response = self._get_client().get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_group_name_is_required(self):
        response = self._get_client().post(self.url)
        self.assertFormError(response, 'form', 'name',
            'This field is required.')

    def test_group_name_cant_be_shorter_than_5(self):
        response = self._get_client().post(self.url, {'name': 'abc'})
        self.assertFormError(response, 'form', 'name',
            'Ensure this value has at least 4 characters (it has 3).')

        response = self._get_client().post(self.url, {'name': 'abcde'})
        self.assertEquals(auth_models.Group.objects.filter(name='abcde').count(), 1)

    def test_group_name_cant_be_longer_than_30(self):
        response = self._get_client().post(self.url, {'name': 'a' * 31})
        self.assertFormError(response, 'form', 'name',
            'Ensure this value has at most 30 characters (it has 31).')

        response = self._get_client().post(self.url, {'name': 'a' * 30})
        self.assertEquals(auth_models.Group.objects.filter(name='a' * 30).count(), 1)

    def test_group_name_must_be_unique(self):
        response = self._get_client().post(self.url, {'name': 'Unique Group'})
        self.assertEquals(auth_models.Group.objects.filter(name='Unique Group').count(), 1)
        response = self._get_client().post(self.url, {'name': 'Unique Group'})
        self.assertFormError(response, 'form', 'name',
            'Group with the same name already exists. Please choose different name.')

    def test_returns_201_on_successfull_creation(self):
        response = self._get_client().post(self.url, {'name': 'abcde'})
        self.assertEquals(response.status_code, 201)

    def test_group_creation_requires_logged_in_user(self):
        c = client.Client()
        response = c.post(self.url, {'name': 'abcde'})
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    def test_adds_admin_to_added_group_on_successfull_creation(self):
        response = self._get_client().post(self.url, {'name': 'abcde'})
        self.assertEquals(response.status_code, 201)
        User.objects.get(username="admin", groups__name="abcde")

    def test_adds_admin_to_added_group_on_successfull_creation(self):
        response = self._get_client_superadmin().post(self.url, {'name': 'abcde'})
        self.assertEquals(response.status_code, 201)
        self.assertRaises(User.DoesNotExist, User.objects.get, username="admin", groups__name="abcde")

    # TODO: group_creation_requires_at_least_admin_role


class ProfileGroupTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/groups/selfregister/'

    def _get_client(self, username='admin', password='admin'):
        return self._get_client_superadmin()

    def _create_group(self, name='Test Group', enabled=False):
        group = auth_models.Group(name=name)
        group.save()
        
        group_profile = models.GroupProfile(group=group,
                self_register_enabled=enabled)
        group_profile.save()
        return group
    
    def _post_json(self, url, data=None, client=None):
        if data is None:
            data = {}

        if client is None:
            client = self._get_client()

        response = client.post(
            url,
            json.dumps(data),
            content_type='application/json')
        return response


    def test_get_request(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 405)

    def test_enable_group(self):
        group = self._create_group()
        group_profile = group.groupprofile
        self.assertEquals(False, group_profile.self_register_enabled)

        data = {"action": "enable", "groups": [group.id]}
        response = self._post_json(self.url, data=data)
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals('OK', data['status'])

        group_profile = models.GroupProfile.objects.get(group=group)
        self.assertEquals(True, group_profile.self_register_enabled)

    def test_disable_group(self):
        group = self._create_group(enabled=True)
        group_profile = group.groupprofile
        self.assertEquals(True, group_profile.self_register_enabled)

        data = {"action": "disable", "groups": [group.id]}
        response = self._post_json(self.url, data=data)
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals('OK', data['status'])

        group_profile = models.GroupProfile.objects.get(group=group)
        self.assertEquals(False, group_profile.self_register_enabled)

    def test_wrong_action(self):
        data = {"action": "wrong", "groups": [1]}
        response = self._post_json(self.url, data=data)
        self.assertEquals(response.status_code, 400)

    def test_enable_not_existing_group(self):
        data = {"action": "enable", "groups": [12345]}
        response = self._post_json(self.url, data=data)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals('ERROR', data['status'])

    def test_disable_not_existing_group(self):
        data = {"action": "disable", "groups": [12345]}
        response = self._post_json(self.url, data=data)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals('ERROR', data['status'])


class EditGroupTest(TestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/groups/'

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def _create_group(self, name='Test Group'):
        group = auth_models.Group(name=name)
        group.save()
        return group

    def test_requesting_non_existing_group_returns_404(self):
        response = self._get_client().get(self.url + 'not-a-number/')
        self.assertEquals(response.status_code, 404)
        response = self._get_client().get(self.url + '31337/')
        self.assertEquals(response.status_code, 404)

    def test_updating_non_existing_group_returns_404(self):
        response = self._get_client().post(self.url + 'not-a-number/')
        self.assertEquals(response.status_code, 404)
        response = self._get_client().post(self.url + '31337/')
        self.assertEquals(response.status_code, 404)

    def test_get_request_returns_form(self):
        group = self._create_group()
        response = self._get_client().get(self.url + str(group.id) + '/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_group_name_must_be_unique(self):
        self._create_group()
        group = self._create_group('Second Test Group')
        response = self._get_client().post(self.url + str(group.id) + '/', {
            'name': 'Test Group',
            })
        self.assertFormError(response, 'form', 'name',
            'Group with the same name already exists. Please choose different name.')

    def test_returns_201_on_successfull_update(self):
        group = self._create_group()
        url = self.url + str(group.id) + '/'
        response = self._get_client().post(url, {
            'name': 'Test Group',
            })
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 201)
        self.assertTrue('id' in data)

    def test_not_changing_name_is_ok(self):
        group = self._create_group()
        url = self.url + str(group.id) + '/'
        response = self._get_client().post(url, {
            'name': 'Test Group',
            })
        self.assertEquals(response.status_code, 201)

    def test_group_creation_requires_logged_in_user(self):
        group = self._create_group()
        url = self.url + str(group.id) + '/'
        c = client.Client()
        response = c.post(url, {
            'name': 'Test Group',
            })
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + url)


class UserTest(ClientTestCase):
    url = '/management/users/'
    fixtures = ('test-users-management.json',)

    def test_uses_proper_template(self):
        c = client.Client()
        self.assertTrue(c.login(username='admin', password='admin'))
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'management/users.html')

    def test_get_request_returns_200(self):
        c = client.Client()
        self.assertTrue(c.login(username='admin', password='admin'))
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)


class CreateUserTest(ClientTestCase):
    url = '/management/users/create/'
    fixtures = ('test-users-management.json',)

    def test_group_must_exist(self):
        response = create_user_over_http(self.url, self._get_client_admin(), group=31337)
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'group',
            forms.UserProfileForm.GROUP_DOES_NOT_EXIST_MSG)

    def test_group_is_required(self):
        response = create_user_over_http(self.url, self._get_client_admin(), group=None)
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'group', 'This field is required.')

    def test_gets_assigned_to_a_group(self):
        response = create_user_over_http(self.url, self._get_client_admin())
        self.assertEquals(response.status_code, 201)
        members = auth_models.Group.objects.filter(pk=1, user__username='username')
        self.assertEquals(members.count(), 1)

    def test_group_profile_gets_created_for_admins(self):
        response = create_user_over_http(self.url, self._get_client_superadmin(),
            role=models.UserProfile.ROLE_ADMIN)
        self.assertEquals(response.status_code, 201)
        data = json.loads(response.content)
        profiles = models.UserGroupProfile.objects.filter(group=1, user=data['id'])
        self.assertEquals(profiles.count(), 1)

    def test_only_superadmin_can_create_admins(self):
        response = create_user_over_http(self.url, self._get_client_admin(),
            role=models.UserProfile.ROLE_ADMIN)
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'role',
            'Select a valid choice. 20 is not one of the available choices.')

    def test_group_profile_does_not_get_created_for_normal_users(self):
        response = create_user_over_http(self.url, self._get_client_admin())
        self.assertEquals(response.status_code, 201)
        data = json.loads(response.content)
        self.assertRaises(
            models.UserGroupProfile.DoesNotExist,
            models.UserGroupProfile.objects.get,
            group=1, user=data['id'])

    def test_admin_gets_half_admin_perms_by_default(self):
        response = create_user_over_http(self.url, self._get_client_superadmin(),
            role=models.UserProfile.ROLE_ADMIN)
        self.assertEquals(response.status_code, 201)
        data = json.loads(response.content)
        profile = models.UserGroupProfile.objects.get(group=1, user=data['id'])
        self.assertEquals(
            profile.access_level,
            models.UserGroupProfile.LEVEL_HALF_ADMIN)

    def test_get_request_returns_form(self):
        response = self._get_client_admin().get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_phone_matches_regex(self):
        response = create_user_over_http(self.url, self._get_client_admin(),
            phone='+11 23s 432')
        self.assertFormError(response, 'form', 'phone',
            forms.UserProfileForm.PHONE_INVALID_MSG)

    def test_phone_not_required(self):
        response = create_user_over_http(self.url, self._get_client_admin(),
            phone=None)
        self.assertEquals(response.status_code, 201)

    def test_successful_post_request_returns_201(self):
        response = create_user_over_http(self.url, self._get_client_admin())
        self.assertEquals(response.status_code, 201)

    def test_username_must_be_unique(self):
        user = create_user()
        response = create_user_over_http(self.url, self._get_client_admin(),
            username = user.username)
        self.assertFormError(response, 'form', 'username',
            'User with such username already exists. Please enter different username.')

    def test_user_creation_requires_admin_role(self):
        response = create_user_over_http(self.url, self._get_client_user())
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    '''def test_language_is_set(self):
        response = create_user_over_http(self.url, self._get_client_admin())
        self.assertEquals(response.status_code, 201)
        user = models.User.objects.get(username='username')
        self.assertEquals(user.get_profile().language, 'fr')'''

class EditUserTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/users/'

    def test_requesting_non_existing_user_returns_404(self):
        response = self._get_client_admin().get(self.url + 'not-a-number/')
        self.assertEquals(response.status_code, 404)

        response = self._get_client_admin().get(self.url + '31337/')
        self.assertEquals(response.status_code, 404)

    def test_updating_non_existing_user_returns_404(self):
        response = create_user_over_http(self.url + 'not-a-number/',
            self._get_client_admin())
        self.assertEquals(response.status_code, 404)

        response = create_user_over_http(self.url + '31337/',
            self._get_client_admin())
        self.assertEquals(response.status_code, 404)

    def test_get_request_returns_form(self):
        user = create_user()
        response = self._get_client_admin().get(self.url + str(user.id) + '/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_normal_users_cannot_edit_other_users(self):
        user = create_user()
        url = self.url + str(user.id) + '/'
        response = create_user_over_http(url, self._get_client_user())
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + url)

    def test_full_admins_can_change_group_profiles(self):
        response = create_user_over_http(CreateUserTest.url,
            self._get_client_superadmin(),
            role=models.UserProfile.ROLE_ADMIN,
            group=2)
        user_id = json.loads(response.content)['id']
        url = self.url + str(user_id) + '/'
        response = create_user_over_http(url, self._get_client_admin(),
            group=2,
            access_level=models.UserGroupProfile.LEVEL_FULL_ADMIN)
        self.assertEquals(response.status_code, 201)
        profiles = models.UserGroupProfile.objects.filter(user=user_id, group=2)
        self.assertEquals(profiles.count(), 1)

    def test_superadmins_can_change_group_profiles(self):
        url = self.url + '3/'
        response = create_user_over_http(url, self._get_client_superadmin(),
            role=models.UserProfile.ROLE_ADMIN, group=2)
        profiles = models.UserGroupProfile.objects.filter(user=3, group=2)
        self.assertEquals(profiles.count(), 1)

    '''def test_superadmins_can_change_language(self):
        url = self.url + '3/'
        response = create_user_over_http(url, self._get_client_superadmin(),
            language='ru')
        user = models.User.objects.get(id=3)
        self.assertEquals(user.get_profile().language, 'ru')'''

    def test_half_admins_cannot_change_group_profiles(self):
        url = self.url + '3/'
        response = create_user_over_http(url, self._get_client_admin(),
            role=models.UserProfile.ROLE_ADMIN, group=1)
        self.assertEquals(response.status_code, 200)
        profiles = models.UserGroupProfile.objects.filter(user=3, group=2)
        self.assertEquals(profiles.count(), 0)


class ActivateUserTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = "/management/users/%d/activate/"

    def test_get_request_returns_405(self):
        c = self._get_client_superadmin()
        response = c.get(self.url % 1)
        self.assertEquals(response.status_code, 405)

    def test_normal_user_cannot_activate_user(self):
        c = self._get_client_user()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 302)

    def test_admin_cannot_activate_user(self):
        c = self._get_client_admin()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 302)

    def test_superadmin_can_activate_user(self):
        c = self._get_client_superadmin()

        user = auth_models.User.objects.get(id=1)
        user.is_active=False
        user.save()
        self.assertFalse(auth_models.User.objects.get(id=1).is_active)
        
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "OK")
        self.assertTrue(auth_models.User.objects.get(id=1).is_active)

class DeactivateUserTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = "/management/users/%d/deactivate/"

    def test_get_request_returns_405(self):
        c = self._get_client_admin()
        response = c.get(self.url % 1)
        self.assertEquals(response.status_code, 405)

    def test_normal_user_cannot_deactivate_user(self):
        c = self._get_client_user()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 302)

    def test_admin_can_deactivate_user(self):
        c = self._get_client_admin()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "OK")
        self.assertFalse(auth_models.User.objects.get(id=1).is_active)

    def test_superadmin_can_deactivate_user(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "OK")
        self.assertFalse(auth_models.User.objects.get(id=1).is_active)

class DeleteUserTest(ClientTestCase):
    url = "/management/users/%d/delete/"
    fixtures = ('test-users-management.json', 'test-tracking.json')

    def test_normal_user_cannot_delete_user(self):
        c = self._get_client_user()
        response = c.post(self.url % 3)
        self.assertEquals(response.status_code, 302)

    def test_superadmin_cannot_be_deleted(self):
        c = self._get_client_admin()
        response = c.post(self.url % 2)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "ERROR")

    def test_should_throw_404_when_user_not_found(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 11231231)
        self.assertEquals(response.status_code, 404)

    def test_admin_should_send_email(self):
        c = self._get_client_admin()
        response = c.post((self.url % 3) + "?send_goodbye_email=true")
        self.assertEquals(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_superadmin_should_send_email(self):
        c = self._get_client_superadmin()
        response = c.post((self.url % 3) + "?send_goodbye_email=true")
        self.assertEquals(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_admin_cannot_be_deleted(self):
        c = self._get_client_admin()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "ERROR")

    def test_admin_should_delete_user(self):
        c = self._get_client_admin()
        response = c.post(self.url % 3)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "OK")
        self.assertRaises(http.Http404, get_object_or_404, auth_models.User, pk=3)

    def test_superadmin_should_delete_user(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 3)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "OK")
        self.assertRaises(http.Http404, get_object_or_404, auth_models.User, pk=3)

    def test_should_not_delete_with_tracking_events(self):
        c = self._get_client_admin()
        response = c.post(self.url % 4)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "ERROR")
        self.assertEquals(json.loads(response.content)["messages"], "User has started course.")

    def test_should_not_delete_with_not_managed_group(self):
        c = self._get_client_admin()
        response = c.post(self.url % 5)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "ERROR")
        self.assertEquals(json.loads(response.content)["messages"], "User has groups not managed by this admin.")

    def test_should_change_course_state_to_assigned_of_unused_course(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 4)
        self.assertEquals(response.status_code, 200)
        course = Course.objects.get(id=1)
        self.assertEquals(course.state_code, ActiveAssign.CODE)

    def test_should_change_course_state_to_deactivated_of_unused_course(self):
        c = self._get_client_superadmin()
        course = Course.objects.get(id=1)
        course.state_code = DeactivatedUsed.CODE
        course.save()

        response = c.post(self.url % 4)
        self.assertEquals(response.status_code, 200)
        course = Course.objects.get(id=1)
        self.assertEquals(course.state_code, Deactivated.CODE)

class DeleteUsersFromCSVTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = "/management/users/delete/"

    def test_normal_user_cannot_delete_users(self):
        c = self._get_client_user()
        response = c.post(self.url)
        self.assertEquals(response.status_code, 302)

    def test_admin_cannot_delete_users(self):
        c = self._get_client_admin()
        response = c.post(self.url)
        self.assertEquals(response.status_code, 302)

    def test_should_handle_fake_and_not_remove_valid_usernames(self):
        c = self._get_client_superadmin()
        f = open("src/management/fixtures/test_delete_users_err.csv")
        response = c.post(self.url, {'file': f})
        f.close()
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['result']['errors']), 1)
        self.assertEquals(len(response.context['result']['infos']), 2)
        self.assertEquals(response.context['result']["row_num"], 3)
        self.assertTemplateUsed(response, 'management/import_csv.html')

        self.assertRaises(http.Http404, get_object_or_404, auth_models.User, username="john")
        self.assertRaises(http.Http404, get_object_or_404, auth_models.User, username="admin")

    def test_should_send_emails_to_removed_users(self):
        c = self._get_client_superadmin()
        f = open("src/management/fixtures/test_delete_users_err.csv")
        response = c.post(self.url, {'file': f, 'send_goodbye_email': True})
        f.close()

        self.assertEquals(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)

    def test_should_handle_finnish_letters(self):
        c = self._get_client_superadmin()
        f = open("src/management/fixtures/test_finnish_letters.csv")
        response = c.post(self.url, {'file': f})
        f.close()
        self.assertTrue(len(response.context['result']['errors']) == 2)

    def test_invalid_file_format_returns_200(self):
        c = self._get_client_superadmin()
        f = open("src/management/fixtures/test-users-management.json")
        response = c.post(self.url, {'file': f})
        f.close()
        self.assertEquals(response.status_code, 200)

    def test_should_not_handle_too_big_file(self):
        c = self._get_client_superadmin()
        f = self.get_too_big_file()
        response = c.post(self.url, {'file': f})
        f.close()
        
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(response.context['result']['errors']) == 1)
        self.assertTrue(len(response.context['result']['infos']) == 0)
        self.assertTemplateUsed(response, 'management/import_csv.html')

    def get_too_big_file(self):
        f = StringIO.StringIO('fake\n' * (settings.MANAGEMENT_CSV_LINES_MAX + 1))
        f.name = 'too_big.csv'
        return f

class UsersGroupsTest(ClientTestCase):
    fixtures = ('test-users-management.json',)

    url = '/management/users/%d/groups/'

    def _get_groups(self, id):
        c = self._get_client_superadmin()
        response = c.get(self.url % id)
        return json.loads(response.content)

    def test_should_return_admin_groups(self):
        groups = self._get_groups(1)
        self.assertEquals(len(groups), 3)

    def test_should_return_superadmin_groups(self):
        groups = self._get_groups(2)
        self.assertEquals(len(groups), 0)

class ListGroupsTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/groups/list/'

    def _get_groups_admin(self, url='/management/groups/list/'):
        c = self._get_client_admin()
        response = c.get(url)
        return json.loads(response.content)

    def _get_groups_superadmin(self, url='/management/groups/list/'):
        c = self._get_client_superadmin()
        response = c.get(url)
        return json.loads(response.content)

    def test_get_returns_groups_number(self):
        groups = self._get_groups_superadmin()
        self.assertEquals(len(groups), 5)

    def test_get_return_my_groups_number_admin(self):
        groups = self._get_groups_admin('/management/groups/list/?my=1')
        self.assertEquals(len(groups), 3)

    def test_get_return_my_groups_number_admin(self):
        groups = self._get_groups_admin('/management/groups/list/?my=0')
        self.assertEquals(len(groups), 5)

    def test_list_view_requires_logged_in_user(self):
        url = self.url
        c = client.Client()
        response = c.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + url)

    def test_list_view_requires_logged_in_admin(self):
        url = self.url
        c = self._get_client_admin()
        response = c.get(url)
        self.assertEquals(response.status_code, 200)


class DeleteGroupTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = "/management/groups/%d/delete/"

    def test_get_request_returns_405(self):
        c = self._get_client_admin()
        response = c.get(self.url % 1)
        self.assertEquals(response.status_code, 405)

    def test_normal_user_cannot_delete_group(self):
        c = self._get_client_user()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 302)

    def test_admin_can_delete_not_empty_group(self):
        c = self._get_client_admin()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "OK")
        self.assertRaises(http.Http404, get_object_or_404, auth_models.Group, pk=1)

    def test_admin_can_delete_empty_group(self):
        c = self._get_client_admin()
        response = c.post(self.url % 3)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "OK")

    def test_superadmin_can_delete_group(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)["status"], "OK")
        self.assertRaises(http.Http404, get_object_or_404, auth_models.Group, pk=1)

    def test_should_throw_404_when_user_not_found(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 11231231)
        self.assertEquals(response.status_code, 404)


class ListUsersTest(TestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/users/list/'

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def _get_list(self, username='admin', password='admin'):
        c = self._get_client(username, password)
        response = c.get(self.url)
        return json.loads(response.content)

    def test_requires_logged_in_user(self):
        c = client.Client()
        response = c.get(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    def test_requires_admin_user(self):
        c = self._get_client(username='john')
        response = c.get(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    def test_grants_access_to_admin_users(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_grants_access_to_superadmin_users(self):
        c = self._get_client(username='superadmin')
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_response_body_is_json(self):
        try:
            self._get_list()
        except ValueError:
            self.fail('Response did not contain valid JSON.')

    def test_includes_admins_in_the_list(self):
        data = self._get_list()
        # The admin user's ID in fixtures is 6
        self.assertTrue('6' in data['users'])

    def test_admin_does_not_see_himself_on_the_list(self):
        data = self._get_list()
        # The admin user's ID in fixtures is 1.
        self.assertFalse('1' in data['users'])

    def test_includes_normal_users_in_the_list(self):
        data = self._get_list()
        # John's ID in fixtures is 3.
        self.assertTrue('3' in data['users'])

    def test_users_have_correct_membership(self):
        data = self._get_list()
        # User john is a member of the Employees group.
        self.assertTrue(3 in data['memberships']['1'])
        # Admin normal_admin is a member of the Employees group.
        self.assertTrue(6 in data['memberships']['2'])
        # Admin normal_admin is a member of the Sales Dept. group.
        self.assertTrue(6 in data['memberships']['4'])
        # Superuser is not a member of any group.
        self.assertFalse(2 in data['memberships']['1'])
        self.assertFalse(2 in data['memberships']['2'])

    def test_mygroups_contains_only_groups_where_current_user_is_full_admin(self):
        data = self._get_list()
        self.assertTrue('1' not in data['mygroups'])
        self.assertTrue('2' in data['mygroups'])

    def test_mygroups_contain_all_groups_for_superadmin(self):
        data = self._get_list(username='superadmin')
        self.assertEquals(len(data['mygroups']), 0)


class AddUserToGroupTest(TestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/groups/%d/members/'

    def _url(self, group_id):
        return self.url % (group_id,)

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def _post_json(self, url, data=None, client=None):
        if data is None:
            data = {}

        if client is None:
            client = self._get_client()

        response = client.post(
            url,
            json.dumps(data),
            content_type='application/json')
        return response

    def test_requires_logged_in_user(self):
        c = client.Client()
        response = c.post(self._url(1))
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self._url(1))

    def test_grants_access_to_admin_users(self):
        response = self._post_json(self._url(1), {
            'action': 'add',
            'members': [],
            })
        self.assertEquals(response.status_code, 200)

    def test_grants_access_to_superadmin_users(self):
        c = self._get_client(username='superadmin')
        response = self._post_json(self._url(1), {
            'action': 'add',
            'members': [],
            },
            client=c)
        self.assertEquals(response.status_code, 200)

    def TODO_test_admins_can_only_add_to_their_groups(self):
        # TODO: Write this test.
        pass

    def TODO_test_half_admins_cannot_modify_membership(self):
        # TODO: Write this test.
        pass

    def TODO_test_superadmins_can_add_to_all_groups(self):
        # TODO: Write this test.
        pass

    def TODO_test_adding_admin_to_new_group_creates_group_profile(self):
        # TODO: Write this test.
        pass

    def TODO_test_default_group_profile_is_half_admin(self):
        # TODO: Write this test.
        pass

    def test_rejects_get_requests(self):
        c = self._get_client()
        response = c.get(self._url(1))
        self.assertEquals(
            response.status_code, 405)

    def test_returns_bad_request_on_non_json_payload(self):
        c = self._get_client()
        response = c.post(self._url(1), 'invalidjson', content_type='application/json')
        self.assertEquals(
            response.status_code,
            http.HttpResponseBadRequest.status_code)

    def __test_response_body_is_json(self):
        try:
            pass
        except ValueError:
            self.fail('Response did not contain valid JSON.')

    def test_adding_to_inexisting_group_results_in_404(self):
        c = self._get_client()
        response = c.post(self._url(31337))
        self.assertEquals(response.status_code, 404)

    def test_adds_users_to_group(self):
        # Add John to Operations.
        response = self._post_json(self._url(3), {
            'action': 'add',
            'members': [3],
            })
        data = json.loads(response.content)
        self.assertEquals(data['status'], 'OK')
        group = auth_models.Group.objects.get(pk=3)
        self.assertEquals(group.user_set.count(), 1)

    def test_removes_users_from_group(self):
        # Remove John from Employees.
        response = self._post_json(self._url(1), {
            'action': 'remove',
            'members': [3],
            })
        data = json.loads(response.content)
        self.assertEquals(data['status'], 'OK')
        group = auth_models.Group.objects.get(pk=1)
        self.assertEquals(group.user_set.count(), 1)

    def test_re_adding_user_is_ok(self):
        user = create_user()
        response = self._post_json(self._url(3), {
            'action': 'add',
            'members': [user.id],
            })
        data = json.loads(response.content)
        self.assertEquals(data['status'], 'OK')
        try:
            auth_models.Group.objects.get(user__id=user.id)
        except auth_models.Group.DoesNotExist:
            self.fail('User was not added to the group.')

    def test_re_removing_user_is_ok(self):
        user = create_user()
        response = self._post_json(self._url(3), {
            'action': 'remove',
            'members': [user.id],
            })
        data = json.loads(response.content)
        self.assertEquals(data['status'], 'OK')
        try:
            auth_models.Group.objects.get(user__id=user.id)
            self.fail('User was not remove from the group.')
        except auth_models.Group.DoesNotExist:
            pass

    def test_adding_inexisting_user_fails(self):
        response = self._post_json(self._url(3), {
            'action': 'add',
            'members': [31337],
            })
        data = json.loads(response.content)
        self.assertEquals(data['status'], 'ERROR')

    def test_removing_inexisting_user_fails(self):
        response = self._post_json(self._url(3), {
            'action': 'remove',
            'members': [31337],
            })
        data = json.loads(response.content)
        self.assertEquals(data['status'], 'ERROR')

    def test_unknown_action_is_a_bad_request(self):
        response = self._post_json(self._url(3), {
            'action': 'INVALID',
            'members': [1],
            })
        self.assertEquals(
            response.status_code,
            http.HttpResponseBadRequest.status_code)


class AddUserToGroupTransactionTest(TransactionTestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/groups/%d/members/'

    def _url(self, group_id):
        return self.url % (group_id,)

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def _post_json(self, url, data=None, client=None):
        if data is None:
            data = {}

        if client is None:
            client = self._get_client()

        response = client.post(
            url,
            json.dumps(data),
            content_type='application/json')
        return response

    def test_add_is_transactional(self):
        user = create_user()
        response = self._post_json(self._url(3), {
            'action': 'add',
            'members': [user.id, 31337],
            })
        data = json.loads(response.content)
        self.assertEquals(data['status'], 'ERROR')
        try:
            auth_models.Group.objects.get(pk=3, user__id=user.id)
            self.fail('User was added to the group.')
        except auth_models.Group.DoesNotExist:
            pass

    def test_remove_is_transactional(self):
        user = create_user()
        g = auth_models.Group.objects.get(pk=3)
        user.groups.add(g)

        response = self._post_json(self._url(3), {
            'action': 'remove',
            'members': [user.id, 31337],
            })
        data = json.loads(response.content)
        self.assertEquals(data['status'], 'ERROR')
        try:
            auth_models.Group.objects.get(pk=3, user__id=user.id)
        except auth_models.Group.DoesNotExist:
            self.fail('User was removed from the group.')


class UsersToCSVExportTest(TestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/groups/%d/members/export/'

    def _url(self, group_id):
        return self.url % (group_id,)

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def test_unexisting_group_returns_404(self):
        c = self._get_client()
        response = c.get(self._url(123))
        self.assertEquals(response.status_code, 404)

    def test_strange_format_returns_400(self):
        c = self._get_client()
        response = c.get(self._url(1)+"?format=123")
        self.assertEquals(response.status_code, 400)

    def test_get_request_status_200(self):
        c = self._get_client()
        response = c.get(self._url(1))
        self.assertEquals(response.status_code, 200)

    def test_get_response_content_type_csv(self):
        c = self._get_client()
        response = c.get(self._url(3))
        self.assertTrue(response['content-type'].startswith('text/csv'))

    def test_get_response_contains_attachment(self):
        c = self._get_client()
        response = c.get(self._url(3))
        content_disp = response['content-disposition']
        self.assertTrue(content_disp.find('attachment;') != -1)


class UsersFromCSVImportTest(TestCase):
    fixtures = ('test-users-management.json', 'test-templates.json')
    url = '/management/groups/%d/members/import/'

    def _url(self, group_id):
        return self.url % (group_id,)

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def test_get_request_returns_form(self):
        c = self._get_client()
        response = c.get(self._url(1))
        self.assertTrue('form' in response.context)

    def test_get_renders_correct_template(self):
        c = self._get_client()
        response = c.get(self._url(1))
        self.assertTemplateUsed(response, 'management/import_csv.html')

    def test_post_renders_correct_template(self):
        c = self._get_client()
        f = open("src/management/fixtures/test.csv")
        response = c.post(self._url(1), {'file': f})
        f.close()
        self.assertTemplateUsed(response, 'management/import_csv.html')

    def test_unexisting_group_returns_404(self):
        c = self._get_client()
        response = c.get(self._url(123))
        self.assertEquals(response.status_code, 404)

    def test_strange_file_format_returns_200(self):
        c = self._get_client()
        f = open("src/management/fixtures/test-users-management.json")
        response = c.post(self._url(1), {'file': f})
        f.close()
        self.assertEquals(response.status_code, 200)

    def test_no_header_fields_in_file_return_200(self):
        c = self._get_client()
        f = open("src/management/fixtures/test_head_err.csv")
        response = c.post(self._url(1), {'file': f})
        f.close()
        self.assertEquals(response.status_code, 200)

    def test_wrong_data_in_file_return_200(self):
        c = self._get_client()
        f = open("src/management/fixtures/test_data_err.csv")
        response = c.post(self._url(1), {'file': f})
        f.close()
        self.assertEquals(response.status_code, 200)

    def test_wrong_data_in_file_return_errors(self):
        c = self._get_client()
        f = open("src/management/fixtures/test_data_err.csv")
        response = c.post(self._url(1), {'file': f})
        f.close()
        self.assertTrue(len(response.context['result']['errors']) > 0)

    def test_good_data_in_file_return_infos(self):
        c = self._get_client()
        f = open("src/management/fixtures/test.csv")
        response = c.post(self._url(1), {'file': f})
        f.close()
        self.assertTrue(len(response.context['result']['infos']) > 0)

    def test_good_data_in_file_return_no_errors(self):
        c = self._get_client()
        f = open("src/management/fixtures/test.csv")
        response = c.post(self._url(1), {'file': f})
        f.close()
        self.assertFalse(response.context['result']['errors'])

    def test_too_big_file_returns_error(self):
        c = self._get_client()
        f = open("src/management/fixtures/test_too_many_lines.csv")
        response = c.post(self._url(1), {'file': f})
        f.close()
        self.assertTrue(response.context['result']['errors'])
        self.assertEquals(response.context['result']['errors'][0],
            'Imported file has more than maximal number of lines (%d)'% (settings.MANAGEMENT_CSV_LINES_MAX,))

class UserProfileTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/users/profile/'

    def test_accepts_get_request(self):
        c = self._get_client_user()
        response = c.post(self.url)
        self.assertEquals(response.status_code, 405)
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_accepts_all_roles(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)
        c = self._get_client_admin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)
        c = self._get_client_superadmin()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_uses_template(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'management/user_profile.html')

class UserPassChangeTest(ClientTestCase):
    fixtures = ('test-users-management.json',)
    url = '/management/users/password/'
    form = forms.ChangePasswordForm

    def test_get_returns_form(self):
        c = self._get_client_user()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_post_accepts_only_own_pass_change(self):
        c = self._get_client_user()
        response = c.post(self.url, {'user_id': 1,
                                     'old_password': 'admin',
                                     'new_password': 'new_pass',
                                     'new_password_rep': 'new_pass'
                                    })
        self.assertEquals(response.status_code, 400)

    def test_post_requires_proper_data(self):
        c = self._get_client_user()
        response = c.post(self.url, {'user_id': 3,
                                     'old_password': 'admin2',
                                     'new_password': 'new_pass',
                                     'new_password_rep': 'new_pass2'
                                    })
        self.assertFormError(response, 'form', 'old_password', self.form.INVALID_OLD_PASS)
        self.assertFormError(response, 'form', None, self.form.DIFFERENT_NEW_PASS)

    def test_post_changes_password_to_given(self):
        c = self._get_client_user()
        response = c.post(self.url, {'user_id': 3,
                                     'old_password': 'admin',
                                     'new_password': 'new_pass',
                                     'new_password_rep': 'new_pass'
                                    })
        self.assertEquals(response.status_code, 200)
        c = self._get_client_user(password='new_pass')
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)


class OneClickLinkTest(ClientTestCase):

    fixtures = ('test-users-management.json', 'test-ocl.json')
    url = "/accounts/ocl/?token=%s"

    def _is_logged(self, c):
        return settings.SESSION_COOKIE_NAME in c.cookies

    def test_should_login_with_valid_token(self):
        c = client.Client()
        response = c.get(self.url % 'XXX')
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self._is_logged(c))
        
        response = c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_should_delete_token_after_login(self):
        c = client.Client()
        response = c.get(self.url % 'XXX')
        self.assertEquals(response.status_code, 302)
        self.assertTrue(len(OneClickLinkToken.objects.all()))
        self.assertTrue(self._is_logged(c))

    def test_should_handle_invalid_token(self):
        c = client.Client()
        response = c.get(self.url % 'FAKE')
        self.assertEquals(response.status_code, 302)
        self.assertFalse(self._is_logged(c))

    def test_should_not_work_for_inactive_user(self):
        User.objects.filter(id=1).update(is_active=False)
        
        c = client.Client()
        response = c.get(self.url % 'XXX')
        self.assertEquals(response.status_code, 302)
        self.assertFalse(self._is_logged(c))

    def test_should_not_work_for_expired_ocl(self):
        c = client.Client()
        response = c.get(self.url % 'YYY')
        self.assertEquals(response.status_code, 200)
        self.assertFalse(self._is_logged(c))
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTrue('ocl_expired' in response.context)

class OneClickLinkExpirationTest(ClientTestCase):

    fixtures = ('test-users-management.json', 'test-ocl.json')
    url = "/management/ocl/%s/expire/"

    def test_expire_now(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 1)
        self.assertEquals(response.status_code, 200)
        from management.models import OneClickLinkToken
        from datetime import date
        ocl = OneClickLinkToken.objects.get(pk=1)
        self.assertTrue(ocl.expired)
        self.assertEquals(ocl.expires_on, date.today())
    
    def test_expire_date(self):
        c = self._get_client_superadmin()
        response = c.post(self.url % 1, {"expires_on": "2032-11-11"})
        self.assertEquals(response.status_code, 200)
        ocl = OneClickLinkToken.objects.get(pk=1)
        self.assertFalse(ocl.expired)
        self.assertEquals(ocl.expires_on, date(2032, 11, 11))


class AdminModulesTest(ClientTestCase):

    fixtures = ('reports-test-users.json', 'reports-test-course.json', 'reports-course-group.json', 'test-reports_scheduler.json')
    url = "/management/admin_modules/?report_id=1"

    def test_should_return_courses_from_all_groups(self):
        lines = list(self._get_client_superadmin().get(self.url).content.splitlines())
        self.assertEquals(1, len(lines))
        self.assertEquals("Super Man", lines[0].split(",")[0])
        self.assertEquals("3", lines[0].split(",")[1])

    def test_should_return_courses_from_admins_groups(self):
        lines = list(self._get_client_admin().get(self.url).content.splitlines())
        self.assertEquals(1, len(lines))
        self.assertEquals("Super Man", lines[0].split(",")[0])
        self.assertEquals("3", lines[0].split(",")[1])

    def test_should_return_proper_content_disposition(self):
        response = self._get_client_superadmin().get(self.url)
        self.assertEquals(response['Content-Disposition'], "attachment; filename=\"admin_modules.csv\"")

class WebServiceLogin(TestCase):
    fixtures = ('test-users-management.json',)

    url = "/webservice/login/"

    def test_no_credentials(self):
        c = client.Client()
        response = c.post(self.url, {})
        data = json.loads(response.content)
        self.assertEquals("ERROR", data['status'])
        self.assertEquals("Invalid credentials", data['message'])

    def test_valid_credentials(self):
        c = client.Client()
        response = c.post(self.url, {'username': 'superadmin', 'password': 'admin'})
        data = json.loads(response.content)
        self.assertEquals(200, response.status_code)
        self.assertEquals("OK", data['status'])
# vim: set et sw=4 ts=4 sts=4 tw=78:
