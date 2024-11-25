from pprint import pprint

from agents.models import HealthPlan, UserData

# Create your views here.
from agents.serializers import (
    GuidedHealthPlanSerializer,
    HealthPlanSerializer,
    ModifiedHealthPlanSerializer,
)
from agents.workflow import Workflow
from analytics.decorators.query import QueryTracker
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class Agents(GenericViewSet):

    def get_serializer_class(self):
        if self.action == "health_plan":
            return HealthPlanSerializer
        if self.action == "modified_health_plan":
            return ModifiedHealthPlanSerializer
        if self.action == "guided_health_plan":
            return GuidedHealthPlanSerializer
        return HealthPlanSerializer

    @QueryTracker.track_query("health_plan")
    def health_plan(self, request, **kwargs):
        """One call to this api intiates the full worklow and returns the final report for the user based on
        user_data"""
        result = {"message": None, "error": None}
        serializer = HealthPlanSerializer
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        print("request data: \n")
        pprint(validated_data)

        try:
            user_data_entry = UserData.objects.create(**validated_data)
        except Exception as e:
            result["error"] = str(e)
            return Response(data=result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            workflow = Workflow(user_data=validated_data)
            initial_plans = workflow.start_workflow()
            result["message"] = initial_plans

            # Save initial plans to the HealthPlan model
            health_plan_entry = HealthPlan.objects.create(
                user=user_data_entry,
                initial_workout_plan=initial_plans["workout_plan"],
                initial_meal_plan=initial_plans["meal_plan"],
                initial_mental_health_tips=initial_plans["wellness_tips"],
            )
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            result["error"] = str(e)
            return Response(data=result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def modified_health_plan(self, request):
        """
        This api returns the workout plan for the user based on the user_data and feedback
        """
        result = {"message": None, "error": None}
        serializer = ModifiedHealthPlanSerializer
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        print("request data: \n")
        pprint(validated_data)

        try:
            user_data_entry = UserData.objects.latest("id")
            user_data = {
                "name": user_data_entry.name,
                "age": user_data_entry.age,
                "weight": user_data_entry.weight,
                "height": user_data_entry.height,
                "fitness_goals": user_data_entry.fitness_goals,
                "dietary_preferences": user_data_entry.dietary_preferences,
                "mental_health_goals": user_data_entry.mental_health_goals,
            }

        except UserData.DoesNotExist:
            result["error"] = "User does not exist"
            return Response(data=result, status=status.HTTP_404_NOT_FOUND)

        try:
            # Retrieve initial plans from the HealthPlan model
            health_plan_entry = HealthPlan.objects.get(user=user_data_entry)

        except HealthPlan.DoesNotExist:
            result["error"] = "Previous record of your Health Plan does not exist"
            return Response(data=result, status=status.HTTP_404_NOT_FOUND)

        try:
            workflow = Workflow(user_data=user_data)
            initial_plans = {
                "workout_plan": health_plan_entry.initial_workout_plan,
                "meal_plan": health_plan_entry.initial_meal_plan,
                "wellness_tips": health_plan_entry.initial_mental_health_tips,
            }
            adjusted_health_plan = workflow.adjust_plans_with_feedback(
                feedback_data=validated_data, initial_plans=initial_plans
            )
            result["message"] = adjusted_health_plan
            return Response(data=result, status=status.HTTP_200_OK)

        except Exception as e:
            result["error"] = str(e)
            return Response(data=result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def guided_health_plan(self, request):
        result = {"message": None, "error": None}
        serializer = GuidedHealthPlanSerializer
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        print("request data:\n")
        pprint(validated_data)

        try:
            user_data = {
                "name": validated_data["name"],
                "age": validated_data["age"],
                "weight": validated_data["weight"],
                "height": validated_data["height"],
                "fitness_goals": validated_data["fitness_goals"],
                "dietary_preferences": validated_data["dietary_preferences"],
                "mental_health_goals": validated_data["mental_health_goals"],
            }

            user_data_entry = UserData.objects.create(**user_data)
            print("saved user data")
        except Exception as e:
            result["error"] = str(e)
            return Response(data=result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            workflow = Workflow(user_data=user_data)
            knowledge_data = {
                "fitness_feedback": validated_data["fitness_feedback"],
                "nutrition_feedback": validated_data["nutrition_feedback"],
                "mental_health_feedback": validated_data["mental_health_feedback"],
            }
            guided_plans = workflow.guided_health_plan_workflow(
                knowledge_data=knowledge_data
            )
            result["message"] = guided_plans

            # Save initial plans to the HealthPlan model
            health_plan_entry = HealthPlan.objects.create(
                user=user_data_entry,
                initial_workout_plan=guided_plans["workout_plan"],
                initial_meal_plan=guided_plans["meal_plan"],
                initial_mental_health_tips=guided_plans["wellness_tips"],
            )
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            result["error"] = str(e)
            return Response(data=result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # create two APIs to expose the query and workflow dbs
