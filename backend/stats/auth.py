from rest_framework import authentication, exceptions

from stats.models import Session, User


class VkSessionAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            session_id = request.COOKIES['session_id']
            session = Session.objects.filter(
                uuid=session_id,
                is_active=True
            ).get()
            user = User.objects.filter(uid=session.user_id).get()
            return user, session
        except (Session.DoesNotExist, User.DoesNotExist, KeyError):
            raise exceptions.AuthenticationFailed("Need auth.")

