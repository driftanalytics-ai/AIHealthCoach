from analytics.views import QueryViewSet, graph_view, metric_info, DetailedAgentView
from django.urls import include, path
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("query", QueryViewSet)
router.register("agent", DetailedAgentView)

urlpatterns = [
    path("graph/", graph_view),
    path("metrics/", metric_info),
    path("", include(router.urls)),
]
print(router.urls)
