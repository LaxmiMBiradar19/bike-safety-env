import os
import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "https://laxmimb-bike-safety-env.hf.space")
MODEL_NAME = os.environ.get("MODEL_NAME", "bike_safety_env")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}


def reset():
    response = requests.post(f"{API_BASE_URL}/reset", headers=headers)
    return response.json()


def step(throttle: float = 0.0, brake: float = 0.0):
    response = requests.post(
        f"{API_BASE_URL}/step",
        json={"throttle": throttle, "brake": brake},
        headers=headers
    )
    return response.json()


if __name__ == "__main__":
    print("Resetting environment...")
    obs = reset()
    print("Observation:", obs)

    print("Taking a step...")
    result = step(throttle=0.5, brake=0.0)
    print("Result:", result)
