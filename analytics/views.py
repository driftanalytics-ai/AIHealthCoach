# Create your views here.
from analytics.models import AgentQuery, Query, Agent
from analytics.serializers import AgentSerializer, EdgeSerializer, QuerySerializer, DetailedAgentSerializer
from analytics.utils.graph import get_master_graph
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from analytics.models import Agent, AgentQuery, Graph, Query
from analytics.serializers import (
    AgentSerializer,
    EdgeSerializer,
    EnrichedGraphSerialier,
    GraphSerializer,
    QuerySerializer,
)
from analytics.utils.graph import get_master_graph


def metric_info(request: HttpRequest):
    if request.method == "GET":
        agent_queries = AgentQuery.objects.all()
        total_tokens = 0
        for aq in agent_queries:
            total_tokens += aq.token_usage
        queries = Query.objects.count()
        completed_queries = Query.objects.filter(completed=True).count()
        response = JsonResponse(
            {
                "total_tokens": total_tokens,
                "cost": (2.5 / 1000000) * total_tokens,
                "total_queries": queries,
                "completed_queries": completed_queries,
                "failed_queries": queries - completed_queries,
            }
        )
        return response


def graph_view(request: HttpRequest):
    if request.method == "GET":
        (agents, edges, interactions) = get_master_graph()
        agent_data = list(AgentSerializer(agents, many=True).data)
        edge_data = EdgeSerializer(edges, many=True).data
        for agent in agent_data:
            if agent.get("name") == "__end__":
                agent_data.append(agent_data.pop(agent_data.index(agent)))
                break
        for edge in edge_data:
            edge["interactions"] = interactions.get(edge["pk"], 0)
        print(agent_data, edge_data)
        response = JsonResponse({"agents": agent_data, "edges": edge_data})
        return response

class DetailedAgentView(ReadOnlyModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = DetailedAgentSerializer

class GraphViewSet(ReadOnlyModelViewSet):
    queryset = Graph.objects.all()
    serializer_class = GraphSerializer

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = EnrichedGraphSerialier(instance)
        ed_total_interactions = dict()
        for q in serializer.data["queries"]:
            for ed in q["graph"]["edges"]:
                if ed["pk"] in ed_total_interactions.keys():
                    ed_total_interactions[ed["pk"]] += ed["interactions"]
                else:
                    ed_total_interactions[ed["pk"]] = ed["interactions"]
        for ed in serializer.data["edges"]:
            ed["interactions"] = ed_total_interactions.get(ed["pk"], 0)
        return Response(serializer.data)


class QueryViewSet(ReadOnlyModelViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by("-id")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        for query in serializer.data:
            for agent in query["graph"]["nodes"]:
                if agent.get("name") == "__end__":
                    query["graph"]["nodes"].append(
                        query["graph"]["nodes"].pop(
                            query["graph"]["nodes"].index(agent)
                        )
                    )
                    break
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        for agent in serializer.data["graph"]["nodes"]:
            if agent.get("name") == "__end__":
                query["graph"]["nodes"].append(
                    query["graph"]["nodes"].pop(query["graph"]["nodes"].index(agent))
                )
                break
        return Response(serializer.data)
