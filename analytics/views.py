# Create your views here.
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from analytics.models import Query
from analytics.serializers import AgentSerializer, EdgeSerializer, QuerySerializer
from analytics.utils.graph import get_master_graph


def graph_view(request: HttpRequest):
    if request.method == "GET":
        (agents, edges, interactions) = get_master_graph()
        agent_data = AgentSerializer(agents, many=True).data
        edge_data = EdgeSerializer(edges, many=True).data
        for edge in edge_data:
            edge["interactions"] = interactions.get(edge["pk"], 0)
        print(agent_data, edge_data)
        response = JsonResponse({"agents": agent_data, "edges": edge_data})
        return response


class QueryViewSet(ReadOnlyModelViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
