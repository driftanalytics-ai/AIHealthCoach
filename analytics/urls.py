from django.urls import include, path
from rest_framework.routers import SimpleRouter

from analytics.views import (
    DetailedAgentView,
    GraphViewSet,
    QueryViewSet,
    agent_tokens,
    get_agent_completed,
    get_query_latency,
    graph_view,
    metric_info,
    token_queries,
)

router = SimpleRouter()
router.register("query", QueryViewSet)
router.register("agent", DetailedAgentView)

router.register("graphs", GraphViewSet)
urlpatterns = [
    path("graph/", graph_view),
    path("metrics/", metric_info),
    path("charts/query_latency/", get_query_latency),
    path("charts/get_agent_comp/", get_agent_completed),
    path("charts/token_queries/", token_queries),
    path("charts/agent_tokens/", agent_tokens),
    path("", include(router.urls)),
]
print(router.urls)
