from rest_framework import serializers


class HealthPlanSerializer(serializers.Serializer):
    # userId = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True)
    age = serializers.IntegerField(required=True)
    gender = serializers.CharField(required=False)
    weight = serializers.FloatField(required=True)
    height = serializers.FloatField(required=True)
    fitness_goals = serializers.CharField(required=True)
    dietary_preferences = serializers.CharField(required=True)
    mental_health_goals = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["gender"].lower() != "male" and attrs["gender"].lower() != "female":
            attrs["gender"] = ""
        return attrs


class ModifiedHealthPlanSerializer(serializers.Serializer):
    fitness_feedback = serializers.CharField()
    nutrition_feedback = serializers.CharField()
    mental_health_feedback = serializers.CharField()


class GuidedHealthPlanSerializer(serializers.Serializer):
    userId = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    age = serializers.IntegerField(required=True)
    gender = serializers.CharField(required=False)
    weight = serializers.FloatField(required=True)
    height = serializers.FloatField(required=True)
    fitness_goals = serializers.CharField(required=True)
    dietary_preferences = serializers.CharField(required=True)
    mental_health_goals = serializers.CharField(required=True)
    fitness_feedback = serializers.CharField(
        required=False, default=None, allow_blank=True
    )
    nutrition_feedback = serializers.CharField(
        required=False, default=None, allow_blank=True
    )
    mental_health_feedback = serializers.CharField(
        required=False, default=None, allow_blank=True
    )

    def validate_gender(self, value):
        if value.lower() == "prefer to not say":
            return ""
        return value

