import json

import psycopg2

from mysite.settings import VK_SERVICE_KEY, DATABASES
from stats.logic.service_api import ServiceVK
from stats.logic.vkapi import VkCore
from stats.models import User


KINDS = {
    'docs': 'delete_docs',
    'wall': 'delete_posts',
    'dialogs': 'delete_dialogs',
    'videos': 'delete_videos',
    'likes_video': 'delete_likes',
    'likes_photo': 'delete_likes',
    'likes_post': 'delete_likes'
}


def get_user_details(username):
    """ Получение информации о пользователе и его access_token """

    # Пытаемся получить супер-токен, если он есть
    extended_token = _get_extended_token(nickname=username)
    svk = ServiceVK(token=VK_SERVICE_KEY)
    # Необходимо получить идентификатор по никнейму
    user_detail = svk.api(
        method='users.get',
        user_ids=username,
        fields='photo_200,photo_max',
        lang='ru'
    )
    user = _find_social_auth_row(user_detail[0]['id'])
    return dict(
        token=(
            extended_token
            if extended_token
            # Добавлена гибкость, так как при использовании разных баз
            # может по разному читаться файл
            else (
                user['extra_data']['access_token']
                if isinstance(user['extra_data'], dict)
                else json.loads(user['extra_data'])['access_token']
            )
        ),
        detail=user_detail[0]
    )


def get_statistics(access_token):
    """ Получение всей статистики """

    # Создадим экземпляр юзера для работы с ВК
    uvk = VkCore(token=access_token)
    stats_dummy = dict(
        count_of_documents=uvk.get_count_of_documents,
        count_of_posts=uvk.get_count_of_posts,
        count_of_videos=uvk.get_count_of_videos,
        count_of_videos_likes=uvk.get_count_of_videos_likes,
        count_of_dialogs=uvk.get_count_of_dialogs,
        count_of_photos_likes=uvk.get_count_of_photos_likes,
        count_of_posts_likes=uvk.get_count_of_posts_likes
    )
    result = {}
    for field, method in stats_dummy.items():
        try:
            data = method()
        except PermissionError:
            data = 'Недоступно!'
        result.update({field: data})
    return result


def attach_extended_token(extra_token, request):
    """ Валидация расширенного токена и сохранение в модели юзера """

    # TODO Ненадежный способ выковыривания токена
    try:
        pure_token = extra_token.split('#')[1].split('&')[0].split('=')[-1]
    except Exception:
        return False

    # Валидация токена через запрос
    uid = _is_valid_token(pure_token, need_user_id=True)
    if not uid:
        return False

    # Сохранение супер токена
    user_obj = User.objects.filter(nickname=request.user.username).first()
    if not user_obj:
        user_obj = User(
            uid=uid,
            nickname=request.user.username,
            extra_token=pure_token,
            fullname=request.user.get_full_name(),

        )
    else:
        user_obj.extra_token = pure_token
    user_obj.save()
    return True


def clear_account(token, kind):
    """ Очистка аккаунта """

    # Создадим экземпляр юзера для работы с ВК
    uvk = VkCore(token=token)
    method_name = KINDS[kind]
    method = getattr(uvk, method_name)
    # Если метод касается удаления лайков
    if method_name.split('_')[-1].endswith('likes'):
        # То небходимо передать, что он будет удалять
        kwarg = {kind.split('_')[-1]: True}
        method(**kwarg)
    else:
        method()


def _get_extended_token(nickname):
    """ Получение расширенного токена пользователя, если такой есть"""

    user = User.objects.filter(nickname=nickname).first()
    if not user:
        return

    # Проверка валидности токена
    if _is_valid_token(user.extra_token):
        return user.extra_token


def _is_valid_token(token, need_user_id=False):
    """ Валидация токена """

    try:
        uvk = VkCore(token=token)
        if not uvk.USER_ID:
            return False
    except PermissionError:
        return False
    if need_user_id:
        return uvk.USER_ID
    return True


def _find_social_auth_row(user_id):
    """ Получение информации о юзере из базы """
    conn = psycopg2.connect(
        dbname=DATABASES['default']['NAME'],
        user=DATABASES['default']['USER'],
        password=DATABASES['default']['PASSWORD'],
        host=DATABASES['default']['HOST']
    )
    cursor = conn.cursor()
    result = {}
    try:
        cursor.execute(
            'SELECT * FROM public.social_auth_usersocialauth WHERE uid = %s',
            (str(user_id),)
        )
        query_result = next((x for x in cursor), [])
        result = {
            y[0]: y[1]
            for y in zip([x.name for x in cursor.description], query_result)
        }
    except Exception:
        pass
    cursor.close()
    conn.close()
    return result
