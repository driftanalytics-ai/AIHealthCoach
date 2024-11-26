import random
import time

import requests


def generate_random_data():
    # Use specific names
    names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey"]
    name = random.choice(names)

    # Randomize age, weight, and height
    age = random.randint(18, 60)
    weight = random.randint(50, 100)
    height = random.randint(140, 200)

    # Randomly choose gender
    gender = random.choice(["male", "female"])

    # Expanded fitness goals
    fitness_goals = random.choice(
        [
            "gain weight and build strength",
            "lose weight and tone muscles",
            "maintain current fitness level",
            "build muscle and increase endurance",
            "enhance flexibility and balance",
            "improve cardiovascular health",
            "gain more muscle and strength for an active lifestyle",
            "reach a personal fitness milestone",
        ]
    )

    # Expanded dietary preferences
    dietary_preferences = random.choice(
        [
            "only meat",
            "vegetarian",
            "vegan",
            "no dietary restrictions",
            "pescatarian",
            "low-carb diet",
            "high-protein diet for muscle gain",
            "balanced diet with minimal sugar",
            "flexitarian with a focus on local produce",
        ]
    )

    # Expanded mental health goals with different word counts
    mental_health_goals = " ".join(
        random.choices(
            [
                "reduce stress",
                "live well",
                "have fun",
                "eat healthy",
                "exercise more",
                "stay positive",
                "improve sleep",
                "focus on mindfulness",
                "build resilience",
                "cultivate gratitude",
                "manage anxiety effectively",
                "create a balanced lifestyle",
                "foster deeper connections",
                "practice self-compassion",
                "be more present",
                "adopt a positive mindset",
                "set and achieve small goals",
            ],
            k=random.randint(5, 15),
        )
    )

    return {
        "name": name,
        "age": age,
        "gender": gender,
        "weight": weight,
        "height": height,
        "fitness_goals": fitness_goals,
        "dietary_preferences": dietary_preferences,
        "mental_health_goals": mental_health_goals,
    }


def make_requests(url, headers, num_requests=100):
    for i in range(num_requests):
        data = generate_random_data()
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"Request {i + 1} succeeded: {response.json()}")
        else:
            print(f"Request {i + 1} failed with status code {response.status_code}")
        time.sleep(0.1)  # Small delay to avoid overwhelming the server


# URL and headers
# url = "https://backend.ebonwinglabs.com/agents/health_plan/"
# url1 = "https://backend.ebonwinglabs.com/agents/health_plan2/"
url = "http://127.0.0.1:8000/agents/health_plan/"
url1 = "https://127.0.0.1:8000/agents/health_plan2/"
headers = {"Content-Type": "application/json"}

# Run the script
make_requests(url, headers, num_requests=10)
make_requests(url1, headers, num_requests=10)
