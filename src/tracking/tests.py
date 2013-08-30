
import json, re
from django.test.testcases import TestCase
from content.course_states import ActiveInUse
from content.models import Segment
from plato_common.test_utils import ClientTestCase, TransactionalClientTestCase
from tracking.models import TrackingEvent, TrackingEventService, module_with_track_ratio
from tracking.utils import progress_formatter

class CreateEventTest(ClientTestCase):
    fixtures = ('test-users-tracking.json', "test-segments.json", "test-course-assign.json")
    url = "/tracking/events/create/"

    def test_should_add_new_event(self):
        c = self._get_client_user()
        response = c.post(self.url,
                          json.dumps({"event_type": TrackingEvent.START_EVENT_TYPE, "segment_id": 1}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(TrackingEvent.objects.get(event_type=TrackingEvent.START_EVENT_TYPE))
        self.assertEquals(Segment.objects.get(pk=1).course.state_code, ActiveInUse.CODE)

    def test_should_add_new_scorm_event(self):
        c = self._get_client_user()
        response = c.post(self.url,
                          json.dumps({"event_type": TrackingEvent.START_EVENT_TYPE, "segment_id": 1,
                                      "is_scorm": "True", "score_raw": "123.23", "score_min": "1.2",
                                      "score_max": "4.2", "lesson_status": "FAKE"}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(TrackingEvent.objects.get(event_type=TrackingEvent.START_EVENT_TYPE).is_scorm)
        self.assertEquals(Segment.objects.get(pk=1).course.state_code, ActiveInUse.CODE)

    def test_should_not_accept_get(self):
         self.should_not_accept_get(self.url)

class UpdateScormEventTest(ClientTestCase):
    fixtures = ('test-users-tracking.json', "test-segments.json", "test-course-assign.json", "test-trackingevents.json")
    url = "/tracking/events/update/"

    def test_can_update_existing_scorm_event(self):
        c = self._get_client_admin()
        response = c.post(self.url,
                          json.dumps({"event_id": 110, "score_max": "100", "score_min": "0", "score_raw": "999", "lesson_status": "complete"}),
                          content_type='application/json')
        self.assertEquals(response.status_code, 200)
        event = TrackingEvent.objects.get(id=111)
        self.assertEquals(event.score_raw, 999)
        self.assertEquals(event.parent_event.id, 110)
        self.assertEquals(event.lesson_status, "complete")

    def test_should_not_accept_get(self):
         self.should_not_accept_get(self.url)
        
class SegmentsTest(TestCase):
    fixtures = ('test-users-tracking.json', "test-segments.json", "test-course-assign.json",
                "course_group-assign.json", "test-trackingevents.json")

    def test_segment_should_be_learnt_if_have_end_event(self):
        data = TrackingEventService().segments(1, 1)
        self.assertFalse(data[0].is_learnt)
        self.assertTrue(data[1].is_learnt)

    def test_segment_should_be_not_learnt_if_have_no_events(self):
        data = TrackingEventService().segments(1, 2)
        self.assertFalse(data[0].is_learnt)
        
    def test_single_segment_should_be_learnt_if_have_end_event(self):
        data = TrackingEventService().segmentIsLearnt(1, 2)
        self.assertTrue(data)
        
    def test_single_segment_should_be_not_learnt_if_have_no_end_event(self):
        data = TrackingEventService().segmentIsLearnt(1, 1)
        self.assertFalse(data)

    def test_single_segment_should_be_not_learnt_if_have_no_events(self):
        data = TrackingEventService().segmentIsLearnt(1, 3)
        self.assertFalse(data)

class ModulesWithTrackingRatioTest(ClientTestCase):
    fixtures = ('test-users-tracking.json', "test-segments.json", "test-course-assign.json",
                "course_group-assign.json", "test-trackingevents.json")
    url = "/tracking/groups/%d/"

    def test_should_handle_active_courses_with_different_ratios(self):
        c = self._get_client_admin()
        response = c.get(self.url % 1)
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data), 3)
        self.assertEquals(data[0]["id"], 1)
        self.assertEquals(data[0]["ratio"], 0.5)
        self.assertEquals(data[1]["id"], 2)
        self.assertEquals(data[1]["ratio"], 0.0)
        self.assertEquals(data[2]["id"], 3)
        self.assertEquals(data[2]["ratio"], 1.0)

    def test_should_handle_course_with_no_segments(self):
        c = self._get_client_admin()
        response = c.get(self.url % 2)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data)
        
class ModuleWithTrackingRatioTest(ClientTestCase):
    fixtures = ('test-users-tracking.json', "test-segments.json", "test-course-assign.json",
                "course_group-assign.json", "test-trackingevents.json")
    
    def test_course_ratio(self):
        data = module_with_track_ratio(1, 1)
        self.assertEquals(data, 0.5)
        data = module_with_track_ratio(1, 2)
        self.assertEquals(data, 0)
        data = module_with_track_ratio(1, 3)
        self.assertEquals(data, 1)
        
class SegmentHistoryTest(ClientTestCase):
    fixtures = ('test-users-tracking.json', "test-segments.json", "test-course-assign.json",
                "course_group-assign.json", "test-trackingevents.json")
    url = "/tracking/modules/%d/segments/%d/"

    def test(self):
        c = self._get_client_admin()
        response = c.get(self.url % (3, 6))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
                
        self.assertEquals(data[0]["duration"], 300)
        self.assertEquals(data[1]["duration"], 300)
        # This will never happen on real application as a pair of START and END events is always created.
        self.assertEquals(data[2]["duration"], "NOT_FINISHED")
        self.assertEquals(data[3]["duration"], 540)

    def test_should_handle_not_existing_segment(self):
        c = self._get_client_user()
        response = c.get(self.url % (2, 123))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data)

class TrackingHistoryTest(TestCase):
    fixtures = ('test-users-tracking.json', "test-segments.json", "test-course-assign.json",
                "course_group-assign.json", "test-trackingevents.json")

    def test_returns_empty_list_if_wrong_participant(self):
        result = TrackingEventService().trackingHistory(segment_id=6, participant_id=2)
        self.assertFalse(result)

    def test_returns_empty_list_if_wrong_segment(self):
        result = TrackingEventService().trackingHistory(segment_id=1000, participant_id=1)
        self.assertFalse(result)

    def test_returns_events_list(self):
        result = TrackingEventService().trackingHistory(segment_id=6, participant_id=1)
        self.assertTrue(result)

    def test_returns_needed_fields(self):
        result = TrackingEventService().trackingHistory(segment_id=6, participant_id=1)
        for elem in result:
            self.assertTrue('date' in elem)
            self.assertTrue('duration' in elem)
            self.assertTrue('result' in elem)

    def test_duration_has_proper_format(self):
        result = TrackingEventService().trackingHistory(segment_id=6, participant_id=1)
        self.assertTrue(re.match("\d{2}:\d{2}:\d{2}", result[0]['duration']))

    def test_returns_proper_number_of_events(self):
        result = TrackingEventService().trackingHistory(segment_id=6, participant_id=1)
        self.assertEquals(len(result), 3)

class ProgressFormatterTest(TestCase):
    
    def test_returns_zero_if_no_progress(self):
        result = progress_formatter(0)
        self.assertEquals(result, 0)
        
    def test_returns_10_if_lt15(self):
        result = progress_formatter(0.01)
        self.assertEquals(result, 10)
        result = progress_formatter(0.149)
        self.assertEquals(result, 10)
        result = progress_formatter(0.15)
        self.assertEquals(result, 20)
        
    def test_returns_round_if_lt95(self):        
        result = progress_formatter(0.249)
        self.assertEquals(result, 20)
        result = progress_formatter(0.25)
        self.assertEquals(result, 30)
        result = progress_formatter(0.849)
        self.assertEquals(result, 80)
        result = progress_formatter(0.85)
        self.assertEquals(result, 90)
        result = progress_formatter(0.949)
        self.assertEquals(result, 90)
        result = progress_formatter(0.95)
        self.assertEquals(result, 90)
        
    def test_returns_90_if_lt100(self):
        result = progress_formatter(0.951)
        self.assertEquals(result, 90)
        result = progress_formatter(0.99999)
        self.assertEquals(result, 90)
        
    def test_returns_1_if_completed(self):
        result = progress_formatter(1)
        self.assertEquals(result, 100)

class TotalTimeTest(ClientTestCase):

    fixtures = ('test-users_tracking.json', "test-segments.json", "test-course-assign.json",
                "course_group-assign.json", "test-trackingevents.json", "test-reports_tracking.json")

    url = "/tracking/total_time/?report_id=%d"

    def test_should_return_courses_from_all_groups(self):
        lines = list(self._get_client_superadmin().get(self.url % 1).content.splitlines())
        self.assertEquals(1, len(lines))
        first_row_tokens=lines[0].split(",")
        self.assertEquals(first_row_tokens[0], "marek zegarek")
        self.assertEquals(first_row_tokens[1], "01:19:00")

    def test_should_return_courses_from_all_groups2(self):
        lines = list(self._get_client_superadmin().get(self.url % 4).content.splitlines())
        self.assertEquals(2, len(lines))
        first_row_tokens=lines[0].split(",")
        second_row_tokens=lines[1].split(",")
        self.assertEquals(first_row_tokens[0], "marek zegarek")
        self.assertEquals(first_row_tokens[1], "01:19:00")
        self.assertEquals(second_row_tokens[0], "John Random")
        self.assertEquals(second_row_tokens[1], "01:00:00")


class ModulesUsageTest(ClientTestCase):

    fixtures = ('test-users-assign.json', "test-segments.json", "test-course-assign.json",
                "course_group-assign.json", "test-trackingevents_tracking.json", "test-reports_tracking.json")

    url = "/tracking/modules_usage/?report_id=%d"

    def test_should_return_only_modules_from_declared_group(self):
        lines = list(self._get_client_superadmin().get(self.url % 4).content.splitlines())
        self.assertEquals(4, len(lines))
        self.assertEquals(lines[0].split(",")[0], "John Random - Praesent pharetra turpis ac turpis pharetra 1.")
        self.assertEquals(lines[1].split(",")[0], "John Random - Praesent pharetra turpis ac turpis pharetra 2.")
        self.assertEquals(lines[2].split(",")[0], "John Random - Praesent pharetra turpis ac turpis pharetra 3.")
        self.assertEquals(lines[3].split(",")[0], "John Random - Praesent pharetra turpis ac turpis pharetra 300.")

    def test_should_return_tracking_for_john(self):
        lines = list(self._get_client_superadmin().get(self.url % 5).content.splitlines())
        self.assertEquals(lines[0].split(",")[0], "John Random")
        self.assertEquals(lines[0].split(",")[1], "01:00:00")

class CourseToContinue(ClientTestCase):

    fixtures = ('test-users-tracking.json', "test-segments.json", "test-course-assign.json",
                "course_group-assign.json", "test-trackingevents.json")

    url = "/tracking/course_to_continue/"

    def test_should_find_completed_course_to_continue(self):
        response = self._get_client_admin().get(self.url)
        self.assertEquals(response.status_code, 404)

    def test_should_find_course_to_continue(self):
        response = self._get_client_user().get(self.url)
        data = json.loads(response.content)
        self.assertEquals(data["segment_id"], 1)
        self.assertEquals(data["course_id"], 1)

    def test_should_not_find_course_to_continue(self):
        response = self._get_client_superadmin().get(self.url)
        self.assertEquals(response.status_code, 404)