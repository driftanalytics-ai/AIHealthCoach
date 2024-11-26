# Create your views here.
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from analytics.models import Agent, AgentQuery, Graph, Query
from analytics.serializers import (
    AgentSerializer,
    DetailedAgentSerializer,
    EdgeSerializer,
    EnrichedGraphSerialier,
    GraphSerializer,
    QuerySerializer,
)
from analytics.utils.graph import get_master_graph


def get_query_latency(request: HttpRequest):
    if request.method == "GET":
        graphs = Graph.objects.all()
        graph_delays = []
        for graph in graphs:
            queries = Query.objects.filter(graph=graph).order_by("-timestamp")
            queries = queries[: max(len(queries), 1000)]

            latencies = []
            for q in queries:
                start = q.timestamp
                end = q.end_timestamp
                if end is None:
                    end = start
                for aq in AgentQuery.objects.filter(queryId=q):
                    end = max(end, aq.endTimestamp)
                latencies.append((end - start).total_seconds())
            graph_delays.append({"graph_name": graph.name, "latencies": latencies})
        response = JsonResponse(graph_delays, safe=False)
        return response


def get_agent_completed(request: HttpRequest):
    if request.method == "GET":
        agent_comp_incomp = dict()
        for agent in Agent.objects.all():
            if agent.name not in agent_comp_incomp.keys():
                agent_comp_incomp[agent.name] = [0, 0]
            agent_queries = AgentQuery.objects.filter(agent=agent)
            for aq in agent_queries:
                if aq.completed:
                    agent_comp_incomp[agent.name][0] += 1
                else:
                    agent_comp_incomp[agent.name][1] += 1
        response = []
        for k, v in agent_comp_incomp.items():
            response.append((k, v[0], v[1]))
        response = JsonResponse(response, safe=False)
        return response


def token_queries(request: HttpRequest):
    if request.method == "GET":
        queries = Query.objects.all().order_by("-timestamp")
        queries = queries[: max(len(queries), 1000)]
        tokens = []
        for q in queries:
            token_count = 0
            for aq in AgentQuery.objects.filter(queryId=q):
                token_count += aq.token_usage
            tokens.append(token_count)
        response = JsonResponse(tokens, safe=False)
        return response


def agent_tokens(request: HttpRequest):
    if request.method == "GET":
        agent_token = dict()
        agents = Agent.objects.all()
        for agent in agents:
            total_tokens = 0
            count = 0
            for aq in AgentQuery.objects.filter(agent=agent):
                total_tokens += aq.token_usage
                count += 1
            agent_token[agent.name] = total_tokens / max(count, 1)
        response = []
        for k, v in agent_token.items():
            response.append([k, v])
        response = JsonResponse(response, safe=False)
        return response


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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by("-id")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        for graph in serializer.data:
            for agent in graph["nodes"]:
                if agent.get("name") == "__end__":
                    graph["nodes"].append(
                        graph["nodes"].pop(graph["nodes"].index(agent))
                    )
                    break
        return Response(serializer.data)

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
        for agent in serializer.data["nodes"]:
            if agent.get("name") == "__end__":
                serializer.data["nodes"].append(
                    serializer.data["nodes"].pop(serializer.data["nodes"].index(agent))
                )
                break
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
