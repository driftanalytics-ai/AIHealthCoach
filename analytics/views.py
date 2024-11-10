# Create your views here.
from analytics.models import Query
from analytics.serializers import AgentSerializer, EdgeSerializer, QuerySerializer
from analytics.utils.graph import get_master_graph
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import Response
from rest_framework.viewsets import ReadOnlyModelViewSet


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
