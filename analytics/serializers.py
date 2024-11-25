from collections import OrderedDict

from rest_framework.relations import PKOnlyObject
from rest_framework.serializers import (
    BaseSerializer,
    ModelSerializer,
    SerializerMethodField,
)

from analytics.models import Agent, AgentQuery, Edge, Graph, Query
from analytics.utils.graph import get_interactions


class AgentSerializer(ModelSerializer):
    class Meta:
        model = Agent
        fields = ["pk", "name", "model_name", "runtime_stats", "token_usage_stats"]
        depth = 2


class EdgeSerializer(ModelSerializer):
    start = AgentSerializer()
    end = AgentSerializer()

    class Meta:
        model = Edge
        fields = ["pk", "start", "end"]
        depth = 2


class GraphSerializer(ModelSerializer):
    nodes = AgentSerializer(many=True)
    edges = EdgeSerializer(many=True)

    class Meta:
        model = Graph
        fields = ["id", "nodes", "edges", "name"]


class AgentQuerySerializer(ModelSerializer):
    agent = AgentSerializer()

    class Meta:
        model = AgentQuery
        fields = [
            "pk",
            "agent",
            "token_usage",
            "startTimestamp",
            "endTimestamp",
            "response",
        ]


class QuerySerializer(ModelSerializer):
    agent_queries = AgentQuerySerializer(source="get_agent_queries", many=True)
    total_tokens = SerializerMethodField()
    enriched_edges = SerializerMethodField()
    graph = GraphSerializer()

    class Meta:
        model = Query
        fields = [
            "id",
            "agent_queries",
            "query_text",
            "timestamp",
            "graph",
            "total_tokens",
            "enriched_edges",
        ]
        depth = 2

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = (
                attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            )
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        ret["graph"]["edges"] = ret["enriched_edges"]
        del ret["enriched_edges"]
        return ret

    def get_total_tokens(self, obj):
        tokens = 0
        for agent_query in AgentQuery.objects.filter(queryId=obj):
            tokens += agent_query.token_usage
        return tokens

    def get_enriched_edges(self, obj: Query):
        edges = obj.graph.edges.get_queryset()
        print(edges)
        agent_queries = AgentQuery.objects.filter(queryId=obj)
        interactions = get_interactions(agent_queries, edges)
        edges = EdgeSerializer(edges, many=True).data
        print(edges)
        for edge in edges:
            edge["interactions"] = interactions.get(edge["pk"], 0)

        return edges


class EnrichedGraphSerialier(ModelSerializer):
    queries = SerializerMethodField()
    edges = EdgeSerializer(many=True)

    class Meta:
        model = Graph
        fields = ["id", "nodes", "edges", "name", "queries"]
        depth = 2

    def get_queries(self, obj: Graph):
        queries = Query.objects.filter(graph=obj)
        serializer = QuerySerializer(queries, many=True)
        return serializer.data
