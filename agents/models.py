from django.db import models


class UserData(models.Model):
    queryId = models.AutoField(primary_key=True)
    userId = models.IntegerField()
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.CharField(max_length=255)
    weight = models.FloatField()
    height = models.FloatField()
    fitness_goals = models.CharField(max_length=255)
    dietary_preferences = models.CharField(max_length=255)
    mental_health_goals = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class HealthPlan(models.Model):
    user = models.OneToOneField(
        UserData, on_delete=models.CASCADE, related_name="health_plan"
    )
    initial_workout_plan = models.JSONField(null=True, blank=True)
    initial_meal_plan = models.JSONField(null=True, blank=True)
    initial_mental_health_tips = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
