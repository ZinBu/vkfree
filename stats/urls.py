
from rest_framework import routers

from stats.views.other import WelcomeViewSet, StatisticsViewSet, \
    ExtendTokenViewSet, ClearViewSet
from stats.views.user import UserViewSet

stats_router = routers.DefaultRouter()

stats_router.register('welcome', WelcomeViewSet, base_name='welcome')
stats_router.register('user', UserViewSet, base_name='user')
stats_router.register('get', StatisticsViewSet, base_name='get_stat')
stats_router.register('send_token', ExtendTokenViewSet, base_name='send_token')
stats_router.register('clear', ClearViewSet, base_name='clear')
