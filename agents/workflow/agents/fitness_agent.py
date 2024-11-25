import json
import os
from pprint import pprint

from agents.utils import count_characters_in_json
from analytics.decorators.agent import AgentTrackers
from django.utils import timezone
from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI
from tavily import TavilyClient


class FitnessAgent:
    def __init__(self, user_data):
        self.user_data = user_data
        self.llm = ChatOpenAI()
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.current_workout_plan = None
        self.adjusted_workout_plan = None
        self.feedback = None
        self.agent_name = "fitness"
        self.tokens_produced = 0

    @AgentTrackers.track_agent("fitness_agent")
    def create_workout_plan(self, **kwargs):
        # context = self.tavily_client.get_search_context(
        #     query=f"workout plan for {self.user_data['age']} year old, {self.user_data['weight']} kg {self.user_data.get('gender', '')} person",
        #     search_depth="advanced",
        # )
        fitness_goals = self.user_data["fitness_goals"].lower()

        prompt = [
            {
                "role": "system",
                "content": "You are a fitness coach. Your task is to create a personalized workout plan based on user data.",
            },
            {
                "role": "user",
                "content": f"User data: {self.user_data}\n"
                f"Create a workout plan for a {self.user_data['age']} year old, {self.user_data['weight']} kg person "
                f"with the goal to {fitness_goals}.\n"
                f"Please return the plan in the following JSON format:\n"
                f'{{"workout_plan": ["Exercise 1", "Exercise 2", "Exercise 3", "Exercise 4"]}}\n',
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
        print("Workout Plan: \n")
        pprint(result)
        return result

    def adjust_workout_plan(self, feedback, current_workout_plan, **kwargs):
        context = self.tavily_client.get_search_context(
            query=f"adjust workout plan based on feedback: {feedback}"
        )
        prompt = [
            {
                "role": "system",
                "content": "You are a fitness coach. Your task is to adjust a workout plan based on user feedback.",
            },
            {
                "role": "user",
                "content": f"Current workout plan: {current_workout_plan}\n"
                f"Additional context: {context}\n"
                f"User feedback: {feedback}\n"
                f"Adjust the workout plan accordingly.\n"
                f"Please return the adjusted plan in the following JSON format:\n"
                f'{{"workout_plan": ["Exercise 1", "Exercise 2", "Exercise 3", "Exercise 4"]}}\n',
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
        print("Adjusted Workout Plan: \n")
        pprint(result)
        return result

    def start(self, feedback=None, **kwargs):
        print("fitness start kwargs", kwargs)
        return_data = dict
        if not feedback:
            self.current_workout_plan = self.create_workout_plan(**kwargs)
            return_data.update({"current_workout_plan": self.current_workout_plan})

        else:
            self.adjusted_workout_plan = self.adjust_workout_plan(
                feedback, self.current_workout_plan, **kwargs
            )
            return_data.update({"current_workout_plan": self.adjusted_workout_plan})
        print("no exception in fitness")
        return return_data


if __name__ == "__main__":
    from pprint import pprint

    user_data = {
        "name": "Prithviraj",
        "age": 25,
        "weight": 186,
        "height": 200,
        "fitness_goals": "weight loss",
    }

    fitness_agent = FitnessAgent(user_data)
    workout_plan = fitness_agent.create_workout_plan()
    print("Generated Workout Plan:\n")
    pprint(workout_plan)
