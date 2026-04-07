from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from environment import BikeSafetyEnv
from models import Observation, Action

app = FastAPI(
    title="Bike Safety Environment",
    description="A two-wheeler safety simulation for the Meta OpenEnv Hackathon.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance
env = BikeSafetyEnv()


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
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }


@app.get("/observation_space")
def observation_space():
    return {
        "type": "Dict",
        "fields": {
            "speed": {"type": "float", "description": "Current speed in km/h"},
            "dist_to_obstacle": {"type": "float", "description": "Distance to obstacle in meters"},
            "road_friction": {"type": "float", "description": "1.0 = dry, 0.6 = wet"}
        }
    }


@app.get("/action_space")
def action_space():
    return {
        "type": "Dict",
        "fields": {
            "throttle": {"type": "float", "min": 0.0, "max": 1.0},
            "brake": {"type": "float", "min": 0.0, "max": 1.0}
        }
    }


@app.get("/")
def root():
    return {
        "name": "Bike Safety Environment",
        "version": "1.0.0",
        "endpoints": ["/reset", "/step", "/observation_space", "/action_space", "/health", "/docs"]
    }