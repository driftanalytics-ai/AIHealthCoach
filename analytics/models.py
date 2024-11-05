from django.db import models
from agents.models import UserData

class Query(models.Model):
    queryId = models.OneToOneField(UserData, on_delete=models.CASCADE, primary_key=True)
    query = models.TextField()  # Stores the query text
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically sets the current timestamp


class Workflow(models.Model):
    queryId = models.ForeignKey(Query, on_delete=models.CASCADE, primary_key=False)  # Related Query
    nodeId = models.IntegerField()  # Node ID
    token_usage = models.IntegerField()  # Token usage for this node
    startTimestamp = models.DateTimeField()
    endTimestamp = models.DateTimeField()
