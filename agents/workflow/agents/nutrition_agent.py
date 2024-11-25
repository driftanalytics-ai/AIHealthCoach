import json
import os
from pprint import pprint

from agents.utils import count_characters_in_json
from analytics.decorators.agent import AgentTrackers
from django.utils import timezone
from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI
from tavily import TavilyClient


class NutritionAgent:
    def __init__(self, user_data):
        self.user_data = user_data
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.current_meal_plan = None
        self.adjusted_meal_plan = None
        self.feedback = None
        self.agent_name = "nutrition"
        self.tokens_produced = 0

    @AgentTrackers.track_agent("nutrition")
    def create_meal_plan(self, **kwargs):
        # context = self.tavily_client.get_search_context(
        #     query=f"meal plan for {self.user_data.get('gender', '')} person who is {self.user_data['age']} year old, weighs {self.user_data['weight']} kg person with dietary preferences: {self.user_data['dietary_preferences']}",
        #     search_depth="advanced",
        # )
        dietary_preferences = self.user_data["dietary_preferences"]
        prompt = [
            {
                "role": "system",
                "content": "You are a nutritionist. Your task is to create a personalized meal plan based on user data.",
            },
            {
                "role": "user",
                "content": f"User data: {self.user_data}\n"
                f"Create a meal plan for a {self.user_data['age']} year old, {self.user_data['weight']} kg person "
                f"with dietary preferences: {dietary_preferences}.\n"
                f"Please return the plan in the following JSON format:\n"
                f'{{"meal_plan": ["Meal 1", "Meal 2", "Meal 3", "Meal 4"]}}\n',
            },
        ]

        lc_messages = convert_openai_messages(prompt)
        optional_params = {"response_format": {"type": "json_object"}}
        response = (
            ChatOpenAI(
                model="gpt-4-0125-preview", max_retries=1, model_kwargs=optional_params
            )
            .invoke(lc_messages)
            .content
        )
        result = json.loads(response)
        print("Generated Meal Plan: \n")
        pprint(result)
        return result

    def adjust_meal_plan(self, feedback):
        context = self.tavily_client.get_search_context(
            query=f"adjust meal plan based on feedback: {feedback}"
        )

        prompt = [
            {
                "role": "system",
                "content": "You are a nutritionist. Your task is to adjust a meal plan based on user feedback.",
            },
            {
                "role": "user",
                "content": f"Current meal plan: {self.current_meal_plan}\n"
                f"Additional context: {context}\n"
                f"User feedback: {feedback}\n"
                f"Adjust the meal plan accordingly.\n"
                f"Please return the adjusted plan in the following JSON format:\n"
                f'{{"meal_plan": ["Meal 1", "Meal 2", "Meal 3", "Meal 4"]}}\n',
            },
        ]

        lc_messages = convert_openai_messages(prompt)
        optional_params = {"response_format": {"type": "json_object"}}
        response = (
            ChatOpenAI(
                model="gpt-4-0125-preview", max_retries=1, model_kwargs=optional_params
            )
            .invoke(lc_messages)
            .content
        )
        result = json.loads(response)
        print("Adjusted Meal Plan: \n")
        pprint(result)
        return result

    def start(self, feedback=None, **kwargs):
        return_data = dict
        if not feedback:
            self.current_meal_plan = self.create_meal_plan(**kwargs)
            return_data.update({"current_meal_plan": self.current_meal_plan})

        else:
            self.adjusted_meal_plan = self.adjust_meal_plan(feedback)
            return_data.update({"current_meal_plan": self.adjusted_meal_plan})
        pprint(return_data)
        return return_data


if __name__ == "__main__":
    from pprint import pprint

    user_data = {
        "name": "Prithviraj",
        "age": 25,
        "weight": 200,
        "height": 186,
        "fitness_goals": "weight loss",
        "dietary_preferences": "vegan",
    }

    nutrition_agent = NutritionAgent(user_data)
    meal_plan = nutrition_agent.create_meal_plan()
    print("Generated Meal Plan:\n")
    pprint(meal_plan, width=120)
