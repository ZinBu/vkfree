from datetime import datetime

from dateutil.relativedelta import relativedelta
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.status import HTTP_406_NOT_ACCEPTABLE, HTTP_423_LOCKED

from mysite.settings import TOKEN_LINK
from stats.logic.processing import get_user_details, get_statistics, \
    attach_extended_token, clear_account
from stats.models import Task
from stats.views.serializers import ExtendTokenSerializer, ClearSerializer


class WelcomeViewSet(viewsets.ViewSet):
    """ Страничка приветствия  """

    def list(self, request):
        return Response(
            data=dict(
                first_name=request.user.first_name,
                photo_link=request.user.photo,
                # Добавим ссылку на токен по расширению прав
                root_app_href=TOKEN_LINK
            )
        )


class StatisticsViewSet(viewsets.ViewSet):
    """ Страничка сбора статистики """

    def list(self, request):
        token = request.user.get_token(request.auth.token)
        stats = get_statistics(token)
        return Response(data=stats)


class ExtendTokenViewSet(viewsets.ViewSet):
    """
    Класс расширения полномочий приложения по отношению к пользователю,
    путем передачи от него расширенного доп. правами токена VK
    """

    def create(self, request):
        extra_token = ExtendTokenSerializer(data=request.data).get('token')

        operation_state = attach_extended_token(extra_token, request)
        if operation_state:
            return Response()

        return Response(status=HTTP_406_NOT_ACCEPTABLE)


class ClearViewSet(viewsets.ViewSet):
    """ Класс очитски какого-либо раздела VK """

    def create(self, request):
        kind = ClearSerializer(data=request.data).get('kind')
        if not request.user.extra_token:
            Response(
                'Need extra token.',
                status=status.HTTP_403_FORBIDDEN
            )
        # TODO Нужно прикручивать Celery (не на бесплатных хостингах)
        # Проверка того, что у юзера нет выполняющейся задачи
        task_state = self._check_and_toggle_task_state(request.user.uid)
        if not task_state:
            return Response(status=HTTP_423_LOCKED)
        try:
            clear_account(token=request.user.extra_token, kind=kind)
        except Exception:
            pass
        # Разблокируем юзера в любом случае
        self._unlock_task(request.user.uid)
        return Response()

    def _check_and_toggle_task_state(self, user_id):
        task = Task.objects.filter(user_id=user_id).first()
        # Если нет таски - создаем
        if not task:
            Task(user_id=user_id, busy=True).save()
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

    def _unlock_task(self, user_id):
        task = Task.objects.filter(user_id=user_id).first()
        task.busy = False
        task.save()
