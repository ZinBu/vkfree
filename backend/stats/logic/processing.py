from mysite.settings import VK_SERVICE_KEY
from stats.logic.service_api import ServiceVK
from stats.logic.vkapi import VkCore
from stats.models import User, Session

KINDS = {
    'docs': 'delete_docs',
    'wall': 'delete_posts',
    'dialogs': 'delete_dialogs',
    'videos': 'delete_videos',
    'likes_video': 'delete_likes',
    'likes_photo': 'delete_likes',
    'likes_post': 'delete_likes'
}


def get_user_details(user_id):
    """ Получение информации о пользователе и его access_token """

    svk = ServiceVK(token=VK_SERVICE_KEY)
    # Необходимо получить идентификатор по никнейму
    user_detail = svk.api(
        method='users.get',
        user_ids=user_id,
        fields='photo_200,photo_max',
        lang='ru'
    )
    return user_detail[0]


def get_statistics(access_token):
    """ Получение всей статистики """

    # Создадим экземпляр юзера для работы с ВК
    uvk = VkCore(token=access_token)
    stats_dummy = dict(
        count_of_documents=uvk.get_count_of_documents,
        count_of_posts=uvk.get_count_of_posts,
        count_of_videos=uvk.get_count_of_videos,
        count_of_videos_likes=uvk.get_count_of_videos_likes,
        # VK ограничло доступ
        # count_of_dialogs=uvk.get_count_of_dialogs,
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

    request.user.extra_token = pure_token
    request.user.save()
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


def add_new_user(data):
    session = Session(user_id=str(data['user_id']), token=data['access_token'])
    session.save()
    user_info = get_user_details(data['user_id'])
    user = User.objects.filter(uid=str(data['user_id'])).first()
    user_photo = user_info.get(
        "photo_200",
        user_info.get("photo_max", '')
    )
    first_name = f"{user_info['first_name']}"
    last_name = f"{user_info['last_name']}"
    if not user:
        user = User(
            first_name=first_name,
            last_name=last_name,
            uid=data['user_id'],
            photo=user_photo
        )
    else:
        user.photo = user_photo
        user.first_name = first_name
        user.last_name = last_name

    user.save()
    return str(session.uuid)


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
