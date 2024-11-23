from analytics.models import Agent, AgentQuery, Edge, Graph, Query
from django.db.models import Case, QuerySet, When
from django.urls import include


def get_master_graph():
    queries = Query.objects.all()
    agents = Agent.objects.get_queryset().none()
    edges = Edge.objects.get_queryset().none()
    edge_interactions = dict()
    for query in queries:
        agent_queries = AgentQuery.objects.filter(queryId=query)
        agent_queries.order_by("startTimestamp")
        for aq in agent_queries:
            print(aq.agent.name)
        agents |= query.graph.agents.get_queryset()
        edges |= query.graph.edges.get_queryset()
        temp_edge_interactions = get_interactions(agent_queries, query.graph.edges)
        for k in temp_edge_interactions:
            if k in edge_interactions:
                edge_interactions[k] += temp_edge_interactions[k]
            else:
                edge_interactions[k] = temp_edge_interactions[k]
    return agents, edges, edge_interactions


def get_interactions(
    agent_queries: QuerySet[AgentQuery], edges: QuerySet[Edge]
) -> dict[int, int]:

    agent_queries_list = list(agent_queries.order_by("startTimestamp"))
    edge_interactions = dict()
    previous_agents = [Agent.objects.get_or_create(name="__start__")[0]]
    for i in range(len(agent_queries_list)):
        to_node = agent_queries_list[i].agent
        for from_agent in previous_agents[::-1]:
            if edges.filter(start=from_agent, end=to_node).exists():
                edge = edges.get(start=from_agent, end=to_node)

                if edge.pk in edge_interactions:
                    edge_interactions[edge.pk] += 1
                else:
                    edge_interactions[edge.pk] = 1

        previous_agents.append(to_node)
    for from_agent in previous_agents[::-1]:
        last_agent = Agent.objects.get_or_create(name="__end__")[0]
        if edges.filter(start=from_agent, end=last_agent).exists():
            edge = edges.get(start=from_agent, end=last_agent)

            if edge.pk in edge_interactions:
                edge_interactions[edge.pk] += 1
            else:
                edge_interactions[edge.pk] = 1

    return edge_interactions
