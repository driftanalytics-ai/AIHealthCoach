# analytics/utils.py
from django.shortcuts import get_object_or_404

from agents.models import UserData

from .init_graph import make_graph
from .models import Agent, AgentQuery, Query


def populate_query_db(user_data_instance, graph):
    """Extracts specific fields from validated data and populates the Query model."""
    # Extract fields

    fitness_goals = user_data_instance.get("fitness_goals", "NULL")
    dietary_preferences = user_data_instance.get("dietary_preferences", "NULL")
    mental_health = user_data_instance.get("mental_health_goals", "NULL")

    # Create a descriptive query based on user data
    query_text = f"Fitness Goals: {fitness_goals}, Dietary Preferences: {dietary_preferences}, Mental Health Goals: {mental_health}"
    gr = make_graph(graph)
    print("HERE")
    # Create a new Query object with the foreign key to UserData
    query, created = Query.objects.get_or_create(query_text=query_text, graph=gr)
    return query.id


def populate_workflow_db(user_data_instance, agent_name, tokens, startTime, endTime):
    """Extracts specific fields from validated data and populates the Query model."""
    # Extract fields
    query_instance, created = Query.objects.get_or_create(
        id=user_data_instance.get("query_id", 1)
    )
    agent, created = Agent.objects.get_or_create(name=agent_name)
    # Create a new Query object with the foreign key to UserData
    agent_query, created = AgentQuery.objects.get_or_create(
        queryId=query_instance,
        agent=agent,
        token_usage=tokens,
        startTimestamp=startTime,
        endTimestamp=endTime,
    )

