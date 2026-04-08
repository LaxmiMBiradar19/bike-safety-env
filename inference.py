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
    task_name = MODEL_NAME

    # START block
    print(f"[START] task={task_name}", flush=True)

    # Reset environment
    reset()

    total_reward = 0.0
    num_steps = 5

    # Run steps
    for i in range(1, num_steps + 1):
        result = step(throttle=0.5, brake=0.0)
        reward = result.get("reward", 0.0)
        total_reward += reward
        done = result.get("done", False)

        # STEP block
        print(f"[STEP] step={i} reward={round(reward, 4)}", flush=True)

        if done:
            break

    score = round(total_reward / num_steps, 4)

    # END block
    print(f"[END] task={task_name} score={score} steps={num_steps}", flush=True)
