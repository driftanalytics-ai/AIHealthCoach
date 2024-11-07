from django.contrib.auth.models import (
    User,
)  # Assumes you're using Django's default User model
from django.db import models

from agents.models import UserData


# todo()
# 1. Average response time of agent
# 2. average token usage
# 3. Cost accoeding to
# 4. Model for each agent
# 5. average interactions and per query interaction
# 6.
class Agent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)


class Edge(models.Model):
    id = models.AutoField(primary_key=True)
    start = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="from_agent"
    )
    end = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="to_agent")


class Graph(models.Model):
    id = models.AutoField(primary_key=True)
    nodes = models.ManyToManyField(Agent)
    edges = models.ManyToManyField(Edge)
    hash = models.CharField(max_length=64, unique=True)


class Query(models.Model):
    id = models.AutoField(primary_key=True)
    # userdata = models.OneToOneField(UserData, on_delete=models.CASCADE)
    query_text = models.TextField()  # Stores the query text
    timestamp = models.DateTimeField(
        auto_now_add=True
    )  # Automatically sets the current timestamp
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, null=True)

    # total tokens
    @property
    def get_agent_queries(self):
        print("HERE")
        return AgentQuery.objects.filter(queryId=self)


class AgentQuery(models.Model):
    queryId = models.ForeignKey(
        Query, on_delete=models.CASCADE, primary_key=False
    )  # Related Query
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)  # Node ID
    token_usage = models.IntegerField()  # Token usage for this node
    startTimestamp = models.DateTimeField()
    endTimestamp = models.DateTimeField()
