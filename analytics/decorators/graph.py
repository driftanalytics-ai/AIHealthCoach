from functools import wraps

from analytics.constants import ANALYTICS_QUERY_ID
from analytics.models import Graph, Query


class MultiAgentTracker:
    def track_graph(graph_name: str):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if ANALYTICS_QUERY_ID in kwargs.keys():
                    attach_graph(kwargs.get(ANALYTICS_QUERY_ID), graph_name)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    raise

            return wrapper

        return decorator


def attach_graph(query_id, graph_name):
    query, _ = Query.objects.get_or_create(id=query_id)
    graph, _ = Graph.objects.get_or_create(name=graph_name)
    query.graph = graph
    query.save()

    print(query, query.graph, "following query graph attached")

    return True
