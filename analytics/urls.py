from django.urls import include, path
from rest_framework.routers import SimpleRouter

from analytics.views import QueryViewSet, general_info, graph_view

router = SimpleRouter()
router.register("query", QueryViewSet)

urlpatterns = [
    path("graph/", graph_view),
    path("general/", general_info),
    path("", include(router.urls)),
]
print(router.urls)
