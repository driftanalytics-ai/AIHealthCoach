from django.urls import include, path
from rest_framework.routers import SimpleRouter

from analytics.views import QueryViewSet, graph_view

router = SimpleRouter()
router.register("query", QueryViewSet)
urlpatterns = [path("graph/", graph_view), path("", include(router.urls))]
print(router.urls)
