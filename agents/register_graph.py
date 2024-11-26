from langgraph.graph import Graph

from agents.workflow.agents import (
    FitnessAgent,
    MentalHealthAgent,
    NutritionAgent,
    ProgressTrackingAgent,
)
from analytics.init_graph import get_or_create_graph


class Workflow:
    def __init__(self, user_data):
        self.user_data = user_data

    def collect_feedback(self, agent_name):
        feedback = input(f"Provide feedback on your {agent_name} plan\n")
        return feedback

    def register_graph1(self, **kwargs):
        # Initialize agents
        fitness_agent = FitnessAgent(self.user_data)
        nutrition_agent = NutritionAgent(self.user_data)
        mental_health_agent = MentalHealthAgent(self.user_data)
        progress_agent = ProgressTrackingAgent(self.user_data)

        # Define a LangGraph graph
        graph = Graph()

        # Add nodes for each agent task
        graph.add_node("fitness_agent", lambda _: fitness_agent.start(**kwargs))
        graph.add_node("nutrition", lambda _: nutrition_agent.start(**kwargs))
        graph.add_node("mental_health", lambda _: mental_health_agent.start(**kwargs))
        graph.add_node(
            "progress_report",
            lambda _: progress_agent.track_progress(
                fitness_agent.current_workout_plan,
                nutrition_agent.current_meal_plan,
                mental_health_agent.wellness_tips,
                **kwargs,
            ),
        )

        # Add edges for initial plan creation and feedback collection
        graph.add_edge("fitness", "nutrition")
        graph.add_edge("nutrition", "mental_health")
        graph.add_edge("mental_health", "progress_report")

        # Set up start and end nodes
        graph.set_entry_point("fitness")
        graph.set_finish_point("progress_report")

        # Compile the graph
        chain = graph.compile()
        get_or_create_graph(graph, "Graph1")

    def register_graph2(self):

        # Initialize agents
        fitness_agent = FitnessAgent(self.user_data)
        nutrition_agent = NutritionAgent(self.user_data)
        mental_health_agent = MentalHealthAgent(self.user_data)
        progress_agent = ProgressTrackingAgent(self.user_data)

        # Define a LangGraph graph
        graph = Graph()

        # Add nodes for each agent task
        graph.add_node("fitness", lambda _: fitness_agent.start(**kwargs))
        graph.add_node("nutrition", lambda _: nutrition_agent.start(**kwargs))
        graph.add_node("mental_health", lambda _: mental_health_agent.start(**kwargs))
        graph.add_node(
            "progress_report",
            lambda _: progress_agent.track_progress(
                fitness_agent.current_workout_plan,
                nutrition_agent.current_meal_plan,
                mental_health_agent.wellness_tips,
                **kwargs,
            ),
        )

        # Add edges for initial plan creation and feedback collection
        graph.add_edge("fitness", "mental_health")
        graph.add_edge("mental_health", "nutrition")
        graph.add_edge("nutrition", "progress_report")

        # Set up start and end nodes
        graph.set_entry_point("fitness")
        graph.set_finish_point("progress_report")

        # Compile the graph
        chain = graph.compile()
        get_or_create_graph(graph, "Graph2")
