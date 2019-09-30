from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.response import Response

from mysite.settings import APP_BASE_URL
from stats.logic.processing import add_new_user
from stats.logic.service_api import VkOauth
from stats.models import Session


class AuthViewSet(generics.RetrieveAPIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        auth_url = VkOauth.generate_authorize_url()
        if 'code' in request.query_params:
            code = request.query_params.get('code')
            data = VkOauth.complete_auth(code)
            if 'access_token' in data:
                session_id = add_new_user(data)
                response = Response(
                    headers={'Location': APP_BASE_URL},
                    status=302
                )
                response.set_cookie('session_id', session_id)
                return response

            return Response(status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(headers={'Location': auth_url}, status=302)


class LogoutViewSet(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        Session.objects.filter(
            user_id=request.user.uid,
            is_active=True
        ).update(
            is_active=False
        )
        return redirect('/')
