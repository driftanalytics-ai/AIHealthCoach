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


class Stats(models.Model):
    average = models.FloatField(default=0)
    min_val = models.FloatField(default=10000000)
    max_val = models.FloatField(default=0)
    standard_deviation = models.FloatField(default=0)
    variance = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    sum_val = models.FloatField(default=0)
    sum_squares_val = models.FloatField(default=0)

    def update_stats(self, val: float):
        self.count += 1

        self.sum_val += val
        self.sum_squares_val += val**2
        # Update average
        self.average = self.sum_val / self.count

        # Update min/max
        self.min_val = min(self.min_val, val)
        self.max_val = max(self.max_val, val)

        # Update variance and standard deviation
        mean = float(self.average)
        variance = (float(self.sum_squares_val) / float(self.count)) - (mean * mean)
        self.standard_deviation = float(float(variance) ** 0.5)
        self.save()


def get_default_stats():
    return Stats.objects.create()


def get_default_stats_id():
    return Stats.objects.create().pk


class Agent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    model_name = models.CharField(max_length=20, default="GPT-4o")
    runtime_stats = models.ForeignKey(
        Stats,
        on_delete=models.CASCADE,
        related_name="runtime_agent",
        default=get_default_stats_id,
    )
    token_usage_stats = models.ForeignKey(
        Stats,
        on_delete=models.CASCADE,
        related_name="token_usage_agent",
        default=get_default_stats_id,
    )


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
    name = models.CharField(max_length=100, unique=True)
    hash = models.CharField(max_length=64, unique=True)


class Query(models.Model):
    id = models.AutoField(primary_key=True)
    # userdata = models.OneToOneField(UserData, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    query_text = models.TextField()  # Stores the query text
    timestamp = models.DateTimeField(
        auto_now_add=True
    )  # Automatically sets the current timestamp
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, null=True)
    request_body = models.TextField(null=True)
    response = models.TextField(null=True)

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
    response = models.TextField(default="DEFAULT_RESPONSE", null=True)
    startTimestamp = models.DateTimeField()
    endTimestamp = models.DateTimeField()
    metadata = models.TextField(null=True)
    completed = models.BooleanField(default=False)
