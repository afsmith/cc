from .models import CUser
 
class CUserModelBackend(object):
    def authenticate(self, username=None, password=None, email=None):
        if email and not username:
            username = email
        try:
            user = CUser.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except CUser.DoesNotExist:
            return None
 
    def get_user(self, user_id):
        try:
            return CUser.objects.get(pk=user_id)
        except CUser.DoesNotExist:
            return None
