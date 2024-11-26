from django.urls import include, path
from rest_framework.routers import SimpleRouter

from analytics.views import (
    DetailedAgentView,
    GraphViewSet,
    QueryViewSet,
    AgentPromptsView,
    graph_view,
    metric_info,
)

router = SimpleRouter()
router.register("query", QueryViewSet)
router.register("agent", DetailedAgentView)

router.register("graphs", GraphViewSet)
urlpatterns = [
    path("graph/", graph_view),
    path("metrics/", metric_info),
    path("prompt/", AgentPromptsView.as_view()),
    path("", include(router.urls)),
]
print(router.urls)
