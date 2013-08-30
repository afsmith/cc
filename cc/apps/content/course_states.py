from datetime import datetime, timedelta
from django.utils.translation import ugettext as _

class InvalidActionError(RuntimeError):
    pass

class InvalidStateCodeError(RuntimeError):
    pass

class Action():

    def __init__(self, name, new_state_class, course):
        self._name = name
        self._new_state = new_state_class(course)
        self._course = course

    def perform(self):
        self._course.state_code = self._new_state.code()
        self._course.save()
        return []

class ActivateAction(Action):

    def __init__(self, name, new_state_class, course):
        Action.__init__(self, name, new_state_class, course)

    def perform(self):
        from cc.apps.content.models import Segment
        from cc.apps.content.models import File

        errors = []
        segments = Segment.objects.filter(course=self._course)
        if segments.count() == 0:
            errors.append(_("At least one segment is required."))

        for segment in segments:
            if segment.file.status == File.STATUS_EXPIRED:
                errors.append(_("""Segment "%s" is expired.""") % segment.file.title)
            if segment.file.status == File.STATUS_REMOVED:
                errors.append(_("""Segment "%s" is removed.""") % segment.file.title)

        if self._course.expires_on and self._course.expires_on < (datetime.now() + timedelta(days=7)).date():
            errors.append(_("'Expires to' date must be at least 1 week forward."))

        if self._course.groups_can_be_assigned_to.count() == 0:
            errors.append(_("Module must have at least one group in \"Can be assigned to\" section."))

        if errors:
            return errors
        else:
            if self._course.state_code == Draft.CODE:
                self._course.published_on = datetime.now()

            return Action.perform(self)

class DeactivateAction(Action):

    def __init__(self, action_name, course):
        Action.__init__(self, action_name, Deactivated, course)

    def perform(self):
        self._course.deactivated_on = datetime.now()

        return Action.perform(self)

class DeactivateUsedAction(Action):

    def __init__(self, action_name, course):
        Action.__init__(self, action_name, DeactivatedUsed, course)

    def perform(self):
        self._course.deactivated_on = datetime.now()

        return Action.perform(self)

class DeleteAction(Action):

    def __init__(self, course):
        self._name = "delete"
        self._course = course

    def perform(self):
        #from reports.models import Report
        Report.objects.filter(course=self._course).update(is_deleted=True, course=None)
        self._course.delete()
        return []

class RemoveAction(Action):

    def __init__(self, course):
        Action.__init__(self, "remove", Removed, course)

    def perform(self):
        #from reports.models import Report
        Report.objects.filter(course=self._course).update(is_deleted=True, course=None)
        return Action.perform(self)

class CourseState():

    def __init__(self, course):
        self._course = course

    def code(self):
        raise NotImplementedError

    def name(self):
        raise NotImplementedError

    def actions(self):
        raise NotImplementedError

    def act(self, action_name):
        for action in self.actions():
            if action._name == action_name:
                return action.perform()
        raise InvalidActionError

    def has_code(self, code):
        return self.code() == code

class Draft(CourseState):

    CODE = 1

    def code(self):
        return self.CODE

    def name(self):
        return "DRAFT"

    def actions(self):
        return [ActivateAction("activate", Active, self._course),
                DeleteAction(self._course)]

class Active(CourseState):

    CODE = 2

    def code(self):
        return self.CODE

    def name(self):
        return "ACTIVE"

    def actions(self):
        return [Action("assign", ActiveAssign, self._course),
                DeactivateAction("expire", self._course),
                Action("back_to_draft", Draft, self._course),
                DeleteAction(self._course)]

class ActiveAssign(CourseState):

    CODE = 3

    def code(self):
        return self.CODE

    def name(self):
        return "ACTIVE - Assign"

    def actions(self):
        return [DeleteAction(self._course),
                Action("remove_assignments", Active, self._course),
                DeactivateAction("deactivate", self._course),
                DeactivateAction("expire", self._course),
                Action("work_done", ActiveInUse, self._course)]

class ActiveInUse(CourseState):

    CODE = 4

    def code(self):
        return self.CODE

    def name(self):
        return "ACTIVE - In use"

    def actions(self):
        return [Action("remove_user", ActiveAssign, self._course),
                DeactivateUsedAction("deactivate", self._course),
                DeactivateUsedAction("expire", self._course)]

class Deactivated(CourseState):

    CODE = 5

    def code(self):
        return self.CODE

    def name(self):
        return "DEACTIVATED"

    def actions(self):
        return [ActivateAction("reactivate", ActiveAssign, self._course),
                DeleteAction(self._course)]

class DeactivatedUsed(CourseState):

    CODE = 6

    def code(self):
        return self.CODE

    def name(self):
        return "DEACTIVATED - Used"

    def actions(self):
        return [ActivateAction("reactivate", ActiveInUse, self._course),
                DeactivateAction("remove_user", self._course),
                RemoveAction(self._course)]

class Removed(CourseState):

    CODE = 7

    def code(self):
        return self.CODE

    def name(self):
        return "Removed"

    def actions(self):
        return []
