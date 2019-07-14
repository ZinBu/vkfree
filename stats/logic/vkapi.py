import math
import random
from time import sleep

import requests


class VkCore:
    """ VK API методы """

    TIMEOUT = 0.35  # Таймаут запроса
    VERSION = '5.84'

    def __init__(self, token):
        self.token = token
        self.USER_ID = self.api("users.get")[0]["id"]

    def api(self, method, **kwargs):
        """
        method: string - VK API method
        **kwargs: key=value - requests params
        """

        if kwargs:
            params = dict(kwargs, v=self.VERSION, access_token=self.token)
        else:
            params = dict(v=self.VERSION, access_token=self.token)

        major_url = "https://api.vk.com/method/"
        request = requests.get(major_url + method, params=params).json()
        sleep(self.TIMEOUT)
        if not request.get('response'):
            raise PermissionError(request.get('error'))
        return request["response"]

    def get_count_of_documents(self):
        """ Возвращает количество документов """

        return self._get_count("docs.get")

    def get_count_of_videos_likes(self):
        """ Возвращает кол-во лайков видео """

        return self._get_count("fave.getVideos")

    def get_count_of_posts(self):
        """ Возвращает количество записей со стены """

        return self._get_count("wall.get")

    def get_count_of_videos(self):
        """ Возвращает количество видео """

        return self._get_count("video.get")

    def get_count_of_dialogs(self):
        """ Возвращает количество диалогов """

        return self._get_count("messages.getDialogs")

    def get_count_of_photos_likes(self):
        """ Возвращает кол-во лайков под фото """

        return self._get_count("fave.getPhotos")

    def get_count_of_posts_likes(self):
        """ Возвращает кол-во лайков постов """
        return self._get_count("fave.getPosts")

    def get_all_documents(self):
        """ Получение всех документов пользователя """

        return self._get_all_objects(
            limit=2000,
            object_count_method=self.get_count_of_documents,
            extend_method=lambda obj: [x for x in obj["items"]],
            api_method="docs.get"
        )

    def get_all_posts(self):
        """ Получение всех документов пользователя """

        return self._get_all_objects(
            limit=100,
            object_count_method=self.get_count_of_posts,
            extend_method=lambda obj: [x for x in obj["items"]],
            api_method="wall.get"
        )

    def get_all_dialogs_ids(self):
        """ Получение id всех диалогов пользователя """

        return self._get_all_objects(
            limit=200,
            object_count_method=self.get_count_of_dialogs,
            extend_method=lambda obj: [
                x["message"]["user_id"] for x in obj["items"]
            ],
            api_method="messages.getDialogs"
        )

    def get_all_photos_likes_ids(self):
        """
        Получение id всех лайков фотографий
        :return: list: [("id", "owner_id"), ...]
        """

        return self._get_all_objects(
            limit=50,
            object_count_method=self.get_count_of_photos_likes,
            extend_method=lambda obj: [
                (x["id"], x["owner_id"]) for x in obj["items"]
            ],
            api_method="fave.getPhotos"
        )

    def get_all_posts_likes_ids(self):
        """
        Получение id всех лайков постов
        :return: list: [("id", "owner_id"), ...]
        """

        return self._get_all_objects(
            limit=100,
            object_count_method=self.get_count_of_posts_likes,
            extend_method=lambda obj: [
                (x["id"], x["owner_id"]) for x in obj["items"]
            ],
            api_method="fave.getPosts"
        )

    def get_all_videos_likes_ids(self):
        """
        Получение id всех лайков видео
        :return: list: [("id", "owner_id"), ...]
        """

        return self._get_all_objects(
            limit=50,
            object_count_method=self.get_count_of_videos_likes,
            extend_method=lambda obj: [
                (x["id"], x["owner_id"]) for x in obj["items"]
            ],
            api_method="fave.getVideos"
        )

    def get_all_videos_ids(self):
        """ Получение id всех видео пользователя """

        return self._get_all_objects(
            limit=200,
            object_count_method=self.get_count_of_videos,
            extend_method=lambda obj: [
                (x["id"], x["owner_id"]) for x in obj["items"]
            ],
            api_method="video.get"
        )

    def get_random_wall_picture(self, group_id):
        """ Возвращает случайную картинку со стены группы """

        max_num = self.api(
            method="photos.get",
            owner_id=group_id,
            count=0
        )
        num = random.randint(1, max_num["response"]["count"])
        photo = self.api(
            method="photos.get",
            owner_id=str(group_id),
            album_id='wall',
            count=1,
            offset=num
        )
        attachment = (
                'photo'
                + str(group_id)
                + '_'
                + str(photo["response"]['items'][0]['id'])
        )
        return attachment

    def _get_offset(self, elements_count, limit):
        """
        Вычисляет количество смещений для запроса
        на основе максимальной длины ответа
        :param elements_count: количество необходимых для получения элементов
        :param limit: максимальное число элементов в ответе
        :return: необходимое количество смещений
        """
        if elements_count >= limit:
            offsets = math.ceil(elements_count / limit)
        else:
            offsets = 1
        return offsets

    def _get_count(self, method: str):
        """ Базовый метод для получения количества """

        return self.api(method, count=0)["count"]

    def _get_all_objects(
            self, limit, object_count_method, extend_method, api_method
    ):
        """ Базовый метод для получения объектов """

        obj_count = object_count_method()
        # Вычисляем количество смещений
        multiplier = 0
        offsets = self._get_offset(obj_count, limit)
        all_objects = []
        # Обходим все объекты
        for i in range(offsets):
            objects = self.api(
                method=api_method,
                count=limit,
                offset=0 + limit * multiplier
            )
            # Объединяем объекты
            all_objects.extend(extend_method(objects))
            multiplier += 1
        return all_objects

    def delete_docs(self, user_id=None):
        """
        Удаление всех документов
        :param user_id: int - id пользователя
        """
        # получение id всех документов
        all_docs = self.get_all_documents()
        docs_ids = {x["id"] for x in all_docs}
        # Определение id пользователя у которого будем удалять
        if not user_id:
            user_id = self.USER_ID
        # Удаление
        for doc_id in docs_ids:
            self.api("docs.delete", doc_id=doc_id, owner_id=user_id)

    def delete_posts(self, user_id=None):
        """
        Удаление всех записей со стены
        :param user_id: int - id пользователя
        """
        # Получение id всех записей
        all_posts = self.get_all_posts()
        posts_ides = sorted({x["id"] for x in all_posts}, reverse=True)
        # Определение id пользователя у которого будем удалять
        if not user_id:
            user_id = self.USER_ID
        # Удаление
        for post_id in posts_ides:
            self.api("wall.delete", post_id=post_id, owner_id=user_id)

    def delete_dialogs(self, user_id=None):
        """
        Удаление всех диалогов
        :param user_id: int - id пользователя
        """
        pass

    def delete_videos(self):
        """
        Удаление всех видео
        """
        # Получение id всех записей
        all_videos = self.get_all_videos_ids()
        # Определение id пользователя у которого будем удалять
        # Удаление
        for video_id, owner_id in all_videos:
            try:
                res = self.api(
                    method='video.delete',
                    video_id=video_id,
                    owner_id=owner_id,
                )
                if res != 1:
                    print(f'Проблема {video_id}')
            except Exception as error:
                print(error)
        return True

    def delete_likes(self, post=False, video=False, photo=False):
        """
        Удаление всех лайков к постам, фотографиям и видео
        """
        # Получение id всех типов лайков
        likes_ids_list = (
            ("post", self.get_all_posts_likes_ids()) if post else (None, []),
            ("video", self.get_all_videos_likes_ids()) if video else (None, []),
            ("photo", self.get_all_photos_likes_ids()) if photo else (None, [])
        )
        # Удаление
        # TODO Сапорт ВК сказал, что у них какие-то траблы
        # TODO в апи при удалении лайков в закрытых сообществах
        for like_type, like_ids in likes_ids_list:
            for like_id, owner_id in like_ids:
                try:
                    self.api(
                        method="likes.delete",
                        item_id=like_id,
                        owner_id=owner_id,
                        type=like_type
                    )
                except PermissionError as error:
                    if error.args[0]['error_code'] == 15:
                        continue
        return True
