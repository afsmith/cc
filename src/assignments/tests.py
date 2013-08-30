
import json
from datetime import date
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.test import client, TestCase
from django.utils import simplejson
from django.core import mail
from assignments.views import _users_per_module
from messages.models import Message
from content import models
from content.course_states import Active, ActiveAssign
from content.models import Course
from management.models import OneClickLinkToken


class GroupCourseAssignmentTest(TestCase):

    fixtures = ['test-users-assign.json', 'test-course-assign.json', 'course_group-assign.json', 'test-templates.json']
    url = '/assignments/group/modules/'

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def _post_json(self, url, data=None):
        if data is None:
            data = {}

        c = self._get_client()

        response = c.post(
            url,
            json.dumps(data),
            content_type='application/json')
        return response

    def test_get_request_returns_json(self):
        c = self._get_client()
        response = c.get(self.url)
        try:
            return simplejson.loads(response.content)
        except ValueError, e:
            self.fail('Error parsing default json response from url: '+self.url)


    def test_returns_group_number(self):
        c = self._get_client()
        response = c.get(self.url)
        parsed = simplejson.loads(response.content)
        #-2 - reserved for special usage
        self.assertEquals(len(parsed.keys()), 4)

    def test_returns_assignments_number(self):
        c = self._get_client()
        response = c.get(self.url)
        parsed = simplejson.loads(response.content)
        self.assertEquals(len(parsed["1"]), 3)
        self.assertEquals(len(parsed["2"]), 1)
        self.assertEquals(len(parsed["3"]), 1)

    def test_returns_short_title(self):
        c = self._get_client()
        response = c.get(self.url)
        parsed = simplejson.loads(response.content)
        self.assertEquals(len(parsed["1"]), 3)
        self.assertTrue('short_title' in parsed['1']['1'])
        self.assertEquals(parsed['1']['1']['short_title'], parsed['1']['1']['title'][:7]+'...')

    def test_returns_owner(self):
        c = self._get_client()
        response = c.get(self.url)
        parsed = simplejson.loads(response.content)
        self.assertEquals(len(parsed["1"]), 3)
        self.assertTrue('owner' in parsed['1']['1'])

    def test_post_request_saves_changed_assignments(self):
        response = self._post_json(self.url, {"assignments": { "1": []}})
        group = auth_models.Group.objects.get(pk=1)
        self.assertEquals(group.course_set.count(), 0)

    def test_post_request_returns_json(self):
        response = self._post_json(self.url, {"assignments": { "1": ["1", "2"]}})
        try:
            return simplejson.loads(response.content)
        except ValueError, e:
            self.fail('Error parsing default json response from url: '+self.url)


    def test_post_request_returns_status_ok(self):
        response = self._post_json(self.url, {"assignments": { "1": ["1", "2"]}})
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'OK')

    def test_post_request_returns_status_ok(self):
        response = self._post_json(self.url, {"assignments": { "1": ["1", "2", "300"]}})
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'OK')

    def test_unassigned_course_gets_saved(self):
        assigned = models.CourseGroup.objects.filter(group__id=1,course__id=300)
        self.assertFalse(assigned)
        response = self._post_json(self.url, {"assignments": { "1": ["1", "2", "300"]}})
        result = simplejson.loads(response.content)
        self.assertEquals(result['status'], 'OK')
        assigned = models.CourseGroup.objects.filter(group__id=1,course__id=300)
        self.assertTrue(assigned)

    def _verify_active_course(self):
        self.assertTrue(Course.objects.get(id=300).get_state().has_code(Active.CODE))

    def _verify_active_assign_course(self):
        self.assertTrue(Course.objects.get(id=300).get_state().has_code(ActiveAssign.CODE))

    def test_simple_course_state_change(self):
       self._post_json(self.url, {"assignments": { "1": []}})
       self._verify_active_course()
       self._post_json(self.url, {"assignments": { "1": ["300"]}})
       self._verify_active_assign_course()

    def test_complex_course_assignment_updates(self):
        self._post_json(self.url, {"assignments": {"1": ["300"], "2": ["300"]}})
        self._verify_active_assign_course()
        self._post_json(self.url, {"assignments": {"1": ["300"], "2": []}})
        self._verify_active_assign_course()
        self._post_json(self.url, {"assignments": {"1": [], "2": ["300"]}})
        self._verify_active_assign_course()
        self._post_json(self.url, {"assignments": {"1": [], "2": []}})
        self._verify_active_course()

    def test_non_json_post_request_status_error(self):
        c = self._get_client()
        response = c.post(self.url, {"assignments": {'test': 'value'}})
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'ERROR')

    def test_post_with_wrong_ids_returns_json(self):
        response = self._post_json(self.url, {"assignments": { "10": ["14", "23"]}})
        try:
            return simplejson.loads(response.content)
        except ValueError, e:
            self.fail('Error parsing default json response from url: '+self.url)


    def test_post_with_wrong_ids_status_error(self):
        response = self._post_json(self.url, {"assignments": { "10": ["14", "23"]}})
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'ERROR')

    def test_post_with_wrong_course_ids_status_error(self):
        response = self._post_json(self.url, {"assignments": { "1": ["14", "23"]}})
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'ERROR')
        self.assertEquals(result['messages'][0], 'Course with ID 14 does not exist.')

    def test_requires_logged_in_admin(self):
        c = self._get_client(username='john', password='admin')
        response = c.get(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    def test_post_request_send_notification_use_ocl_expiration_date(self):
        response = self._post_json(self.url, {
            "assignments": { "1": ["1", "2", "300"]},
            "add_one_click_link": "checked",
            "is_sendmail": "checked",
            "expires_on": "2012-11-22",
            })
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'OK')
        self.assertEquals(len(mail.outbox), 1)
        
        msgs = Message.objects.filter(
                recipient=auth_models.User.objects.get(username="john"),
                messageprofile__courses__id=300,
                )
        self.assertEquals(msgs.count(), 1)
        self.assertEquals(msgs[0].messageprofile_set.all()[0].ocl.expires_on,
                date(2012, 11, 22))

    def test_post_request_send_notification_use_ocl_no_expiration_date(self):
        response = self._post_json(self.url, {
            "assignments": { "1": ["1", "2", "300"]},
            "add_one_click_link": "checked",
            "is_sendmail": "checked",
            "expires_on": "",
            })
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'OK')
        self.assertEquals(len(mail.outbox), 1)
        
        msgs = Message.objects.filter(
                recipient=auth_models.User.objects.get(username="john"),
                messageprofile__courses__id=300,
                )
        self.assertEquals(msgs.count(), 1)
        self.assertEquals(msgs[0].messageprofile_set.all()[0].ocl.expires_on,
                None)
    
    def test_post_request_without_send_notification(self):
        response = self._post_json(self.url, {
            "assignments": { "1": ["1", "2", "300"]},
            "is_sendmail": "",
            })
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'OK')
        self.assertEquals(len(mail.outbox), 0)
        
    def test_post_request_send_notification_wihout_ocl(self):
        response = self._post_json(self.url, {
            "assignments": { "1": ["1", "2", "300"]},
            "add_one_click_link": "",
            "is_sendmail": "checked",
            "expires_on": "",
            })
        result = simplejson.loads(response.content)
        self.assertTrue(result['status'], 'OK')
        self.assertEquals(len(mail.outbox), 1)
        
        msgs = Message.objects.filter(
                recipient=auth_models.User.objects.get(username="john"),
                messageprofile__courses__id=300,
                )
        self.assertEquals(msgs.count(), 1)
        self.assertEquals(msgs[0].messageprofile_set.all()[0].ocl, None)
    

class UserModulesListTest(TestCase):

    fixtures = ['test-users-assign.json', 'test-course-assign.json', 'course_group-assign.json']
    url = '/assignments/user/modules/'

    def _get_client(self, username='john', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def test_requires_normal_user(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_doesnt_accept_admins(self):
        c = self._get_client(username='admin')
        response = c.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_response_contains_courses(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue('courses' in response.context)

    def test_returns_all_active_assigned_modules(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue('courses' in response.context)
        self.assertEquals(len(response.context['courses']), 2)

    def test_response_uses_template(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'assignments/user_modules.html')


class AdminStatusTest(TestCase):

    fixtures = ['test-users-assign.json', 'test-course-assign.json', 'course_group-assign.json']
    url = '/'

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def test_uses_correct_template(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTemplateUsed(response, 'assignments/admin_status.html')

    def test_result_has_groups_list_if_admin(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue('groups' in response.context)

    def test_result_has_admin_groups_if_admin(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue('groups' in response.context)
        self.assertEquals(len(response.context['groups']), 2)

    def test_result_has_groups_list_if_superadmin(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue('groups' in response.context)

    def test_result_has_all_groups_if_superadmin(self):
        c = self._get_client(username='superadmin')
        response = c.get(self.url)
        self.assertTrue('groups' in response.context)
        self.assertEquals(len(response.context['groups']), 3)

    def test_result_has_data(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue('data' in response.context)

    def test_result_has_data_for_group(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue(response.context['data'][response.context['groups'][0]])

    def test_result_has_data_and_groups_courses(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue(response.context['data'][response.context['groups'][0]])
        
        #removed due to performance issues
        #self.assertTrue('courses' in response.context['data'][response.context['groups'][0]])

    def test_result_has_data_and_groups_users_data(self):
        c = self._get_client()
        response = c.get(self.url)
        self.assertTrue(response.context['data'][response.context['groups'][0]])
        self.assertTrue('users_data' in response.context['data'][response.context['groups'][0]])

class UserProgressTest(TestCase):

    fixtures = ['test-users-assign.json', 'test-course-assign.json', 'course_group-assign.json', 'test-segments.json', 'test-trackingevents.json', 'test-downloadevent.json']
    url = '/assignments/user/progress/?user_id=%s&course_id=%s'

    def _get_client(self, username='admin', password='admin'):
        c = client.Client()
        self.assertTrue(c.login(username=username, password=password))
        return c

    def test_normal_user_not_permitted(self):
        c = self._get_client(username='john', password='admin')
        response = c.get(self.url %(100, 1))
        self.assertEquals(response.status_code, 302)

    def test_post_request_returns_405(self):
        c = self._get_client()
        response = c.post(self.url %(100, 1))
        self.assertEquals(response.status_code, 405)

    def test_unexisting_user_id_returns_404(self):
        c = self._get_client()
        response = c.get(self.url %(100, 1))
        self.assertEquals(response.status_code, 404)

    def test_unexisting_course_id_returns_404(self):
        c = self._get_client()
        response = c.get(self.url %(1, 100))
        self.assertEquals(response.status_code, 404)

    def test_successfull_response_returns_status_200(self):
        c = self._get_client()
        response = c.get(self.url %(1, 1))
        self.assertEquals(response.status_code, 200)

    def test_response_contains_user_obj(self):
        c = self._get_client()
        response = c.get(self.url %(1, 1))
        self.assertTrue('user_obj' in response.context)

    def test_response_contains_course(self):
        c = self._get_client()
        response = c.get(self.url %(1, 1))
        self.assertTrue('course' in response.context)

    def test_response_contains_segments(self):
        c = self._get_client()
        response = c.get(self.url %(1, 1))
        self.assertTrue('segments' in response.context)

    def test_response_segments_has_all_segments(self):
        c = self._get_client()
        response = c.get(self.url %(1, 1))
        self.assertEquals(len(response.context['segments']), 3)

    def test_response_segments_is_dict(self):
        c = self._get_client()
        response = c.get(self.url %(1, 1))
        self.assertTrue(isinstance(response.context['segments'], dict))

    def test_reponse_segment_has_download_count(self):
        c = self._get_client()
        response = c.get(self.url %(1, 1))
        self.assertTrue('download_count' in response.context['segments'][1])
        self.assertEquals(1, response.context['segments'][1]['download_count'])

class UserPerModuleTest(TestCase):

    fixtures = ['reports-test-users.json', 'reports-test-course.json', 'reports-course-group.json']

    def test_should_return_courses_for_admin_groups(self):
        result = _users_per_module(1)

        self.assertEquals(3, len(result))
        self.assertEquals(result[1]["users_count"], '1')
        self.assertEquals(result[2]["users_count"], '1')
        self.assertEquals(result[3]["users_count"], '2')

    def test_should_return_courses_for_admin_groups_with_defined_group(self):
        result = _users_per_module(1, 1)

        self.assertEquals(2, len(result))
        self.assertEquals(result[1]["users_count"], '1')
        self.assertEquals(result[2]["users_count"], '1')

    def test_should_return_courses_from_all_groups(self):
        result = _users_per_module(2)

        self.assertEquals(4, len(result))
        self.assertEquals(result[1]["users_count"], '1')
        self.assertEquals(result[2]["users_count"], '1')
        self.assertEquals(result[3]["users_count"], '2')
        self.assertEquals(result[300]["users_count"], '1')
