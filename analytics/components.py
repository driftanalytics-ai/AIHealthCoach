# analytics/utils.py
from agents.models import UserData
from django.shortcuts import get_object_or_404

from .init_graph import make_graph
from .models import Agent, AgentQuery, Query, Stats


def populate_query_db(user_data_instance):
    """Extracts specific fields from validated data and populates the Query model."""
    # Extract fields

    fitness_goals = user_data_instance.get("fitness_goals", "NULL")
    dietary_preferences = user_data_instance.get("dietary_preferences", "NULL")
    mental_health = user_data_instance.get("mental_health_goals", "NULL")

    # Create a descriptive query based on user data
    query_text = f"Fitness Goals: {fitness_goals}, Dietary Preferences: {dietary_preferences}, Mental Health Goals: {mental_health}"
    print("HERE")
    # Create a new Query object with the foreign key to UserData
    query = Query.objects.create(query_text=query_text)
    return query.id


def update_graph(id, graph):
    gr = make_graph(graph)
    query = Query.objects.get(id=id)
    query.graph = gr
    query.save()


def populate_workflow_db(
    user_data_instance, agent_name, tokens, startTime, endTime, response
):
    """Extracts specific fields from validated data and populates the Query model."""
    # Extract fields
    query_instance, created = Query.objects.get_or_create(
        id=user_data_instance.get("query_id", 1)
    )

    agent, created = Agent.objects.get_or_create(name=agent_name)
    if created:
        agent.runtime_stats = Stats.objects.create()
    if agent.name == "progress_report":
        query_instance.completed = True
        query_instance.save()
    time_taken = (endTime - startTime).total_seconds()
    update_stats(agent.runtime_stats, time_taken)
    update_stats(agent.token_usage_stats, tokens)
    # Create a new Query object with the foreign key to UserData
    agent_query, created = AgentQuery.objects.get_or_create(
        queryId=query_instance,
        agent=agent,
        token_usage=tokens,
        startTimestamp=startTime,
        endTimestamp=endTime,
        response=response,
    )


def update_stats(stats: Stats, val: float):
    stats.count += 1

    stats.sum_val += val
    stats.sum_squares_val += val**2
    # Update average
    stats.average = stats.sum_val / stats.count

    # Update min/max
    stats.min_val = min(stats.min_val, val)
    stats.max_val = max(stats.max_val, val)

    # Update variance and standard deviation
    mean = float(stats.average)
    variance = (float(stats.sum_squares_val) / float(stats.count)) - (mean * mean)
    stats.standard_deviation = float(float(stats.variance) ** 0.5)
    stats.save()
