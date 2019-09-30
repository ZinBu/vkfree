import requests

from mysite.settings import attrs
from stats.logic.vkapi import VkCore


class ServiceVK(VkCore):
    def __init__(self, token):
        self.token = token


class VkOauth:
    AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
    ACCESS_TOKEN_URL = 'https://oauth.vk.com/access_token'
    CLIENT_ID = attrs['VK_APP']['ID']
    CLIENT_SECRET = attrs['VK_APP']['SECRET']
    REDIRECT_URL = attrs['APP_BASE_URL'] + '/api/auth'
    SCOPE = (
        'wall',
        'friends',
        'photos',
        'video',
        'docs',
        'notes',
        'pages',
        'status',
        'groups',
        'notifications',
    )

    @classmethod
    def generate_authorize_url(cls):
        scope = '+'.join(cls.SCOPE)
        params = '&'.join((
            f"client_id={cls.CLIENT_ID}",
            f"redirect_uri={cls.REDIRECT_URL}",
            f"display=page",
            f"scope={scope}",
            f"v={VkCore.VERSION}",
            f"response_type=code",
        ))
        return f"{cls.AUTHORIZE_URL}?{params}"

    @classmethod
    def complete_auth(cls, code):
        access_url = cls._generate_access_url(code)
        response = requests.get(access_url)
        return response.json()

    @classmethod
    def _generate_access_url(cls, code):
        params = '&'.join((
            f"client_id={cls.CLIENT_ID}",
            f"redirect_uri={cls.REDIRECT_URL}",
            f"client_secret={cls.CLIENT_SECRET}",
            f"code={code}"
        ))
        return f"{cls.ACCESS_TOKEN_URL}?{params}"
