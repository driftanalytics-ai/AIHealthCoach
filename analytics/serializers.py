from collections import OrderedDict

from rest_framework.relations import PKOnlyObject
from rest_framework.serializers import (
    BaseSerializer,
    ModelSerializer,
    SerializerMethodField,
)

from analytics.models import Agent, AgentQuery, Edge, Query
from analytics.utils.graph import get_interactions


class AgentSerializer(ModelSerializer):
    class Meta:
        model = Agent
        fields = ["pk", "name"]


class EdgeSerializer(ModelSerializer):
    class Meta:
        model = Edge
        fields = ["pk", "start", "end"]
        depth = 2


class AgentQuerySerializer(ModelSerializer):
    class Meta:
        model = AgentQuery
        fields = ["agent", "token_usage", "startTimestamp", "endTimestamp"]
        depth = 2


class QuerySerializer(ModelSerializer):
    agent_queries = AgentQuerySerializer(source="get_agent_queries", many=True)
    total_tokens = SerializerMethodField()
    enriched_edges = SerializerMethodField()

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
