from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

from langgraph.graph import Graph

from agents.workflow.agents import (
    FitnessAgent,
    MentalHealthAgent,
    NutritionAgent,
    ProgressTrackingAgent,
)
from analytics.decorators.graph import MultiAgentTracker


class Workflow:
    def __init__(self, user_data):
        self.user_data = user_data

    def collect_feedback(self, agent_name):
        feedback = input(f"Provide feedback on your {agent_name} plan\n")
        return feedback

    @MultiAgentTracker.track_graph("Graph1")
    def start_workflow(self, **kwargs):
        print("User data: \n")
        print(self.user_data)

        self.user_data["query_id"] = id
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
        graph.add_edge("fitness", "nutrition")
        graph.add_edge("nutrition", "mental_health")
        graph.add_edge("mental_health", "progress_report")

        # Set up start and end nodes
        graph.set_entry_point("fitness")
        graph.set_finish_point("progress_report")

        # Compile the graph
        chain = graph.compile()
        # call to the components.py function - query db
        # Execute the graph for each query in parallel
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda _: chain.invoke({}), [{}]))
        print("results", results)
        return_data = {
            "workout_plan": results[0]["fitness"]["workout_plan"],
            "meal_plan": results[0]["nutrition"]["meal_plan"],
            "wellness_tips": results[0]["mental_health"]["wellness_tips"],
        }

        return return_data

    def adjust_plans_with_feedback(self, feedback_data, initial_plans):
        print("User data: \n")
        print(self.user_data)
        print("Feedback data: \n")
        print(feedback_data)

        # Initialize agents
        fitness_agent = FitnessAgent(self.user_data)
        nutrition_agent = NutritionAgent(self.user_data)
        mental_health_agent = MentalHealthAgent(self.user_data)
        progress_agent = ProgressTrackingAgent(self.user_data)

        fitness_feedback = feedback_data.get("fitness_feedback")
        nutrition_feedback = feedback_data.get("nutrition_feedback")
        mental_health_feedback = feedback_data.get("mental_health_feedback")

        workout_plan = initial_plans["workout_plan"]
        meal_plan = initial_plans["meal_plan"]
        wellness_tips = initial_plans["wellness_tips"]
        fitness_agent.current_workout_plan = workout_plan
        nutrition_agent.current_meal_plan = meal_plan
        mental_health_agent.wellness_tips = wellness_tips

        # Define a LangGraph graph
        graph = Graph()

        # Add nodes for each agent task
        graph.add_node(
            "fitness",
            lambda x: (
                fitness_agent.start(fitness_feedback)
                if fitness_feedback
                else fitness_agent.current_workout_plan
            ),
        )
        graph.add_node(
            "nutrition",
            lambda x: (
                nutrition_agent.start(nutrition_feedback)
                if nutrition_feedback
                else nutrition_agent.current_meal_plan
            ),
        )
        graph.add_node(
            "mental_health",
            lambda x: (
                mental_health_agent.start(mental_health_feedback)
                if mental_health_feedback
                else mental_health_agent.wellness_tips
            ),
        )
        graph.add_node(
            "progress_report",
            lambda _: progress_agent.track_progress(
                fitness_agent.current_workout_plan,
                nutrition_agent.current_meal_plan,
                mental_health_agent.wellness_tips,
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

        # Execute the graph for each query in parallel
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda _: chain.invoke({}), [{}]))
        return_data = {
            "workout_plan": results[0]["fitness"],
            "meal_plan": results[0]["nutrition"],
            "wellness_tips": results[0]["mental_health"]["wellness_tips"],
        }
        return return_data

    def guided_health_plan_workflow(self, knowledge_data):
        # Initialize agents
        fitness_agent = FitnessAgent(self.user_data)
        nutrition_agent = NutritionAgent(self.user_data)
        mental_health_agent = MentalHealthAgent(self.user_data)
        progress_agent = ProgressTrackingAgent(self.user_data)

        fitness_feedback = knowledge_data.get("fitness_feedback")
        nutrition_feedback = knowledge_data.get("nutrition_feedback")
        mental_health_feedback = knowledge_data.get("mental_health_feedback")

        fitness_agent.feedback = fitness_feedback
        nutrition_agent.feedback = nutrition_feedback
        mental_health_agent.feedback = mental_health_feedback

        # Define a LangGraph graph
        graph = Graph()

        # Add nodes for each agent task
        graph.add_node("fitness", lambda _: fitness_agent.start())
        graph.add_node(
            "adjust_fitness",
            lambda x: (
                fitness_agent.start(fitness_feedback)
                if fitness_feedback
                else fitness_agent.current_workout_plan
            ),
        )
        graph.add_node("nutrition", lambda _: nutrition_agent.start())
        graph.add_node(
            "adjust_nutrition",
            lambda x: (
                nutrition_agent.start(nutrition_feedback)
                if nutrition_feedback
                else nutrition_agent.current_meal_plan
            ),
        )
        graph.add_node("mental_health", lambda _: mental_health_agent.start())
        graph.add_node(
            "adjust_mental_health",
            lambda x: (
                mental_health_agent.start(mental_health_feedback)
                if mental_health_feedback
                else mental_health_agent.wellness_tips
            ),
        )
        graph.add_node(
            "progress_report",
            lambda _: progress_agent.track_progress(
                fitness_agent.current_workout_plan,
                nutrition_agent.current_meal_plan,
                mental_health_agent.wellness_tips,
            ),
        )

        # Add edges for initial plan creation and feedback collection
        graph.add_edge("fitness", "adjust_fitness")
        graph.add_edge("adjust_fitness", "nutrition")
        graph.add_edge("nutrition", "adjust_nutrition")
        graph.add_edge("adjust_nutrition", "mental_health")
        graph.add_edge("mental_health", "adjust_mental_health")
        graph.add_edge("adjust_mental_health", "progress_report")

        # Conditional edge for fitness feedback
        graph.add_conditional_edges(
            source="fitness",
            path=lambda _: "adjust_fitness" if fitness_feedback else "nutrition",
            path_map={"adjust_fitness": "adjust_fitness", "nutrition": "nutrition"},
        )

        # Conditional edge for nutrition feedback
        graph.add_conditional_edges(
            source="nutrition",
            path=lambda _: (
                "adjust_nutrition" if nutrition_feedback else "mental_health"
            ),
            path_map={
                "adjust_nutrition": "adjust_nutrition",
                "mental_health": "mental_health",
            },
        )

        # Conditional edge for mental health feedback
        graph.add_conditional_edges(
            source="mental_health",
            path=lambda _: (
                "adjust_mental_health" if mental_health_feedback else "progress_report"
            ),
            path_map={
                "adjust_mental_health": "adjust_mental_health",
                "progress_report": "progress_report",
            },
        )

        # Set up start and end nodes
        graph.set_entry_point("fitness")
        graph.set_finish_point("progress_report")

        # Compile the graph
        chain = graph.compile()

        # Execute the graph for each query in parallel
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda _: chain.invoke({}), [{}]))

        return_data = {
            "workout_plan": results[0]["fitness"]["workout_plan"],
            "meal_plan": results[0]["nutrition"]["meal_plan"],
            "wellness_tips": results[0]["mental_health"]["wellness_tips"],
        }

        return return_data
