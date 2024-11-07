import json
import os
from pprint import pprint

from django.utils import timezone
from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

from agents.utils import count_characters_in_json
from analytics.components import populate_workflow_db


class MentalHealthAgent:
    def __init__(self, user_data):
        self.user_data = user_data
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.wellness_tips = None
        self.feedback = None
        self.agent_name = "mental_health"
        self.tokens_produced = 0

    def provide_wellness_tips(self, feedback=None):
        mental_health_goals = self.user_data["mental_health_goals"]

        if not feedback:
            context = self.tavily_client.get_search_context(
                query=f"wellness tips for {self.user_data['age']} year old {self.user_data.get('gender', '')} person with goal to {self.user_data['mental_health_goals']}",
                search_depth="advanced",
            )

            prompt = [
                {
                    "role": "system",
                    "content": "You are a mental health coach. Your task is to provide wellness tips based on user data.",
                },
                {
                    "role": "user",
                    "content": f"User data: {self.user_data}\n"
                    f"Additional context: {context}\n"
                    f"Provide mental wellness tips for someone looking to {mental_health_goals}.\n"
                    f"Please return the tips in the following JSON format:\n"
                    f'{{"wellness_tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4"]}}\n',
                },
            ]
        else:
            prompt = [
                {
                    "role": "system",
                    "content": "You are a mental health coach. Your task is to provide wellness tips based on user data.",
                },
                {
                    "role": "user",
                    "content": f"User data: {self.user_data}\n"
                    f"Previously provided wellnes tips: {self.wellness_tips}\n"
                    f"Provide mental wellness tips for someone looking to {mental_health_goals}.\n"
                    f"The user has provided feedback on the previously provided wellness tips: {feedback}\n"
                    f"Please return the tips in the following JSON format:\n"
                    f'{{"wellness_tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4"]}}\n',
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
        print("Wellness Tip: \n")
        pprint(result)
        return result

    def start(self, feedback=None):
        startTime = timezone.now()

        return_data = dict
        if not feedback:
            self.wellness_tips = self.provide_wellness_tips()
            endTime = timezone.now()
            self.tokens_produced = count_characters_in_json(self.wellness_tips) // 4
            return_data.update({"wellness_tip": self.wellness_tips})
        else:
            self.wellness_tips = self.provide_wellness_tips(feedback)
            self.tokens_produced = count_characters_in_json(self.wellness_tips) // 4
            return_data.update({"wellness_tip": self.wellness_tips})
        populate_workflow_db(
            self.user_data, self.agent_name, self.tokens_produced, startTime, endTime
        )
        return return_data


if __name__ == "__main__":
    from pprint import pprint

    user_data = {
        "name": "Prithviraj Murthy",
        "age": 25,
        "mental_health_goals": "gain muscle and lose fat at the same time",
    }

    mental_health_agent = MentalHealthAgent(user_data)
    wellness_tips = mental_health_agent.provide_wellness_tips()
    print("Mental Wellness Tips:\n")
    pprint(wellness_tips, width=120)
