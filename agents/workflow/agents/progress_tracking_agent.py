import json
import os
from pprint import pprint

from agents.utils import count_characters_in_json
from analytics.decorators.agent import AgentTrackers
from django.utils import timezone
from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI
from tavily import TavilyClient


class ProgressTrackingAgent:
    def __init__(self, user_data):
        self.user_data = user_data
        self.llm = ChatOpenAI()
        self.progress = {}
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.agent_name = "progress_report"
        self.tokens_produced = 0

    @AgentTrackers.track_agent("progress_report")
    def track_progress(
        self, fitness_feedback, nutrition_feedback, mental_health_feedback, **kwargs
    ):
        self.progress["fitness"] = fitness_feedback
        self.progress["nutrition"] = nutrition_feedback
        self.progress["mental_health"] = mental_health_feedback
        return self.progress

    def generate_report(self):
        # context = self.tavily_client.get_search_context(
        #     query=f"progress report for {self.user_data['name']} with feedback: Fitness: {self.progress['fitness']}, Nutrition: {self.progress['nutrition']}, Mental Health: {self.progress['mental_health']}"
        # )

        report_prompt = [
            {
                "role": "system",
                "content": "You are a progress tracking agent. Your task is to generate a progress report based on user feedback.",
            },
            {
                "role": "user",
                "content": f"User data: {self.user_data}\n"
                f"Feedback: Fitness: {self.progress['fitness']}, Nutrition: {self.progress['nutrition']}, "
                f"Mental Health: {self.progress['mental_health']}.\n"
                f"Generate a progress report.\n"
                f"Please return the report in the following JSON format:\n"
                f'{{"progress_report": "Report content"}}\n',
            },
        ]

        lc_messages = convert_openai_messages(report_prompt)
        optional_params = {"response_format": {"type": "json_object"}}
        response = (
            ChatOpenAI(
                model="gpt-4-0125-preview", max_retries=1, model_kwargs=optional_params
            )
            .invoke(lc_messages)
            .content
        )
        result = json.loads(response)
        print("Progress Report: \n")
        pprint(result)
        return result

    def start(self):
        startTime = timezone.now()
        return_data = dict
        return_data.update({"progress": self.generate_report()})
        endTime = timezone.now()
        print("PROGRESS REPORT EMITTED")
        self.tokens_produced = count_characters_in_json(self.return_data) // 4
        return return_data


if __name__ == "__main__":
    from pprint import pprint

    user_data = {"name": "Prithviraj Murthy", "age": 25}

    progress_agent = ProgressTrackingAgent(user_data)
    progress = progress_agent.track_progress("good", "needs improvement", "excellent")
    report = progress_agent.generate_report()
    pprint(report)
