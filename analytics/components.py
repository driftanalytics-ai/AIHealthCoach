# analytics/utils.py
from .models import Query
from .models import Workflow
from agents.models import UserData
from django.shortcuts import get_object_or_404

def populate_query_db(user_data_instance):
    """Extracts specific fields from validated data and populates the Query model."""
    # Extract fields

    fitness_goals = user_data_instance.fitness_goals
    dietary_preferences = user_data_instance.dietary_preferences
    mental_health = user_data_instance.mental_health_goals

    # Create a descriptive query based on user data
    query_text = f"Fitness Goals: {fitness_goals}, Dietary Preferences: {dietary_preferences}, Mental Health Goals: {mental_health}"

    # Create a new Query object with the foreign key to UserData
    query = Query.objects.create(
        queryId=user_data_instance,
        query=query_text
    )

def populate_workflow_db(user_data_instance, nodeId, tokens, startTime, endTime):
    """Extracts specific fields from validated data and populates the Query model."""
    # Extract fields
    query_instance = Query.objects.get(queryId=user_data_instance.get("queryId", []))

    # Create a new Query object with the foreign key to UserData
    workflow = Workflow.objects.create(
        queryId=query_instance,
        nodeId=nodeId,
        token_usage=tokens,
        startTimestamp=startTime,
        endTimestamp=endTime
    )