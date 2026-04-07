from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from environment import BikeSafetyEnv
from models import Observation, Action
import uvicorn

app = FastAPI(title="Bike Safety Environment", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

env = BikeSafetyEnv()

@app.get("/")
def root():
    return {"name": "Bike Safety Environment", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    obs = env.reset()
    return {"observation": obs.dict()}

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {"observation": obs.dict(), "reward": reward, "done": done, "info": info}

@app.get("/observation_space")
def observation_space():
    return {"type": "Dict", "fields": {"speed": {"type": "float"}, "dist_to_obstacle": {"type": "float"}, "road_friction": {"type": "float"}}}

@app.get("/action_space")
def action_space():
    return {"type": "Dict", "fields": {"throttle": {"type": "float", "min": 0.0, "max": 1.0}, "brake": {"type": "float", "min": 0.0, "max": 1.0}}}

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
