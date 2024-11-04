# analytics/utils.py
from .models import Query
from django.utils import timezone

def populate_query_db(validated_data):
    """Extracts specific fields from validated data and populates the Query model."""
    # Extract fields
    userId = validated_data.get("userId", [])
    fitness_goals = validated_data.get("fitness_goals", [])
    dietary_preferences = validated_data.get("dietary_preferences", [])
    mental_health = validated_data.get("mental_health", [])
    
    # Populate Query model
    Query.objects.create(
        user=userId,
        query={
            "fitness_goals": fitness_goals,
            "dietary_preferences": dietary_preferences,
            "mental_health": mental_health,
        },
        timestamp=timezone.now()
    )
