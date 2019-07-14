from django.contrib.auth import logout
from django.shortcuts import redirect
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response


class RegisterViewSet(generics.RetrieveAPIView):
    """
    Страничка регистрации через соц. сеть
    """
    renderer_classes = (TemplateHTMLRenderer,)
    permission_classes = []

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/stats/welcome/')
        return Response(template_name='register.html')


class RouterViewSet(generics.RetrieveAPIView):
    """
    Маршрутизатор пользователей от корня сайта
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/stats/welcome/')
        else:
            return redirect('/register/')


class LogoutViewSet(generics.RetrieveAPIView):
    """
    Выход
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/register/')
