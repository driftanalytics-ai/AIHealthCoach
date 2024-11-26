from django.urls import include, path
from rest_framework.routers import SimpleRouter

from analytics.views import (
    DetailedAgentView,
    GraphViewSet,
    QueryViewSet,
    AgentPromptsView,
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
    path("prompt/", AgentPromptsView.as_view()),
    path("charts/querylatency/", get_query_latency),
    path("charts/agentcompleteness/", get_agent_completed),
    path("charts/querytokens/", token_queries),
    path("charts/agenttokens/", agent_tokens),
    path("", include(router.urls)),
]
print(router.urls)
