from datetime import datetime

from dateutil.relativedelta import relativedelta
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_406_NOT_ACCEPTABLE, HTTP_423_LOCKED

from mysite.settings import TOKEN_LINK
from stats.logic.processing import get_user_details, get_statistics, \
    attach_extended_token, clear_account
from stats.models import Task
from stats.views.serializers import ClearSerializer, ExtendTokenSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """ Класс аутентификации для упразднения проверки CSRF токена """

    def enforce_csrf(self, request):
        return


class WelcomeViewSet(viewsets.ViewSet):
    """ Страничка приветствия  """

    renderer_classes = (TemplateHTMLRenderer,)

    def list(self, request):
        user = get_user_details(request.user.username)
        return Response(
            data=dict(
                first_name=request.user.first_name,
                photo_link=user["detail"].get(
                    "photo_200",
                    user["detail"].get("photo_max", '')
                )
            ),
            template_name='statistics.html'
        )


class StatisticsViewSet(viewsets.ViewSet):
    """ Страничка сбора статистики """

    renderer_classes = (TemplateHTMLRenderer,)

    def list(self, request):
        user = get_user_details(request.user.username)
        stats = get_statistics(user['token'])
        # Добавим аватар юзера
        stats.update(
            photo_link=user["detail"].get(
                "photo_200",
                user["detail"].get("photo_max", '')
            )
        )
        # Добавим ссылку на токен по расширению прав
        stats.update(root_app_href=TOKEN_LINK)
        return Response(data=stats, template_name='statistics_complete.html')


class ExtendTokenViewSet(viewsets.ViewSet):
    """
    Класс расширения полномочий приложения по отношению к пользователю,
    путем передачи от него расширенного доп. правами токена VK
    """

    authentication_classes = (CsrfExemptSessionAuthentication,)

    def create(self, request):
        extra_token = ExtendTokenSerializer(data=request.data).get('token')

        operation_state = attach_extended_token(extra_token, request)
        if operation_state:
            return Response()

        return Response(status=HTTP_406_NOT_ACCEPTABLE)


class ClearViewSet(viewsets.ViewSet):
    """ Класс очитски какого-либо раздела VK """

    authentication_classes = (CsrfExemptSessionAuthentication,)

    def create(self, request):
        kind = ClearSerializer(data=request.data).get('kind')

        # TODO Нужно прикручивать Celery (не на бесплатных хостингах)
        # Проверка того, что у юзера нет выполняющейся задачи
        task_state = self._check_and_toggle_task_state(request.user.username)
        if not task_state:
            return Response(status=HTTP_423_LOCKED)
        try:
            user = get_user_details(request.user.username)
            clear_account(token=user['token'], kind=kind)
        except Exception:
            pass
        # Разблокируем юзера в любом случае
        self._unlock_task(request.user.username)
        return Response()

    def _check_and_toggle_task_state(self, username):
        task = Task.objects.filter(nickname=username).first()
        # Если нет таски - создаем
        if not task:
            Task(nickname=username, busy=True).save()
            return True
        # Если таска есть
        else:
            # Если в состоянии занятости, запрещаем
            # дальнейшую работу
            if task.busy:
                # Также проверим, что заблокирована не больше 30 минут
                time_criteria = datetime.now() - relativedelta(minutes=30)
                if task.updated.replace(tzinfo=None) < time_criteria:
                    task.save()
                    return True
                return False
            # Если свободна - делаем занятой
            # и разрешаем дальнейшую работу
            else:
                task.busy = True
                task.save()
                return True

    def _unlock_task(self, username):
        task = Task.objects.filter(nickname=username).first()
        task.busy = False
        task.save()
