from django.urls import include, path

from stats.urls import stats_router
from stats.views.registration import AuthViewSet, LogoutViewSet

urlpatterns = (
    path('api/auth/', AuthViewSet.as_view()),
    path('api/logout/', LogoutViewSet.as_view()),
    path('api/', include(stats_router.urls))
)
