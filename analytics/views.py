# Create your views here.
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import views
from django.db.models import F
from collections import defaultdict

from analytics.models import Agent, AgentQuery, Graph, Query
from analytics.serializers import (
    AgentSerializer,
    DetailedAgentSerializer,
    EdgeSerializer,
    EnrichedGraphSerialier,
    GraphSerializer,
    QuerySerializer,
    AgentPromptSerializer
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

class AgentPromptsView(views.APIView):
    def get(self, request):
        # Query to get prompts with their queryIds, grouped by agent and prompt
        agent_prompts = AgentQuery.objects.exclude(prompt__isnull=True) \
            .values('agent', 'prompt', 'queryId')
        
        # Group the results
        grouped_prompts = defaultdict(lambda: {
            'agent': None,
            'prompts': defaultdict(list)
        })
        
        for entry in agent_prompts:
            agent = entry['agent']
            prompt = entry['prompt']
            queryId = entry['queryId']
            
            # Populate agent details
            if grouped_prompts[agent]['agent'] is None:
                grouped_prompts[agent]['agent'] = agent
            
            # Add queryId to the corresponding prompt
            prompt_details = grouped_prompts[agent]['prompts']
            
            # Check if prompt exists, if not create a new entry
            prompt_entry = next((p for p in prompt_details[prompt] if p['prompt'] == prompt), None)
            if not prompt_entry:
                prompt_details[prompt].append({
                    'prompt': prompt,
                    'queryIds': [queryId]
                })
            else:
                if queryId not in prompt_entry['queryIds']:
                    prompt_entry['queryIds'].append(queryId)
        
        # Prepare final response by converting defaultdict to list
        response_data = []
        for agent_info in grouped_prompts.values():
            agent_response = {
                'agent': agent_info['agent'],
                'prompts': list(agent_info['prompts'].values())[0]  # Flatten the nested defaultdict
            }
            response_data.append(agent_response)
        
        # Serialize and return
        serializer = AgentPromptSerializer(response_data, many=True)
        return Response(serializer.data)

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
