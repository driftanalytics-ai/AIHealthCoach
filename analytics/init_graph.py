from hashlib import sha256

from langgraph.graph import Graph

from .models import Agent, Edge
from .models import Graph as GraphModel
from .models import Stats


def make_graph(graph: Graph):
    start_agent, created = Agent.objects.get_or_create(name="__start__")
    if created:
        start_agent.runtime_stats = Stats.objects.create()
    end_agent, created = Agent.objects.get_or_create(name="__end__")
    if created:
        end_agent.runtime_stats = Stats.objects.create()
    agents = Agent.objects.get_queryset().filter(id__in=[start_agent.id, end_agent.id])
    agent_names = []
    for node in graph.nodes:
        print(node)
        agent, created = Agent.objects.get_or_create(name=node)
        if created:
            agent.runtime_stats = Stats.objects.create()
        agent.save()
        agent = Agent.objects.get_queryset().filter(id=agent.id)
        agents |= agent
        agent_names.append(node)
    edges = Edge.objects.none()
    print(graph.edges)
    edges_names = []
    for edge in graph.edges:
        print(edge[0], edge[1])
        agent1, agent2 = agents.get(name=edge[0]), agents.get(name=edge[1])
        edge_our, created = Edge.objects.get_or_create(start=agent1, end=agent2)
        edge_our.save()
        edge_our = Edge.objects.get_queryset().filter(id=edge_our.id)
        edges |= edge_our
        edges_names.append(edge[0] + edge[1])
    agent_names.sort()
    edges_names.sort()
    hash_inp = "Vertices: " + ",".join(agent_names) + "Edges: " + ",".join(edges_names)
    hasher = sha256()
    hasher.update(hash_inp.encode("utf-8"))
    hsh = hasher.hexdigest()
    print(str(hsh))
    graph_our, created = GraphModel.objects.get_or_create(hash=hsh)
    if not created:
        return graph_our
    for node in agents:
        graph_our.agents.add(node)
    for edge in edges:
        graph_our.edges.add(edge)
    graph_our.save()
    for node in agents:
        node.save()
    for edge in edges:
        edge.save()
    return graph_our
