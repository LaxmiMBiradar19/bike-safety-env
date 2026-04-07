import random
from models import Observation, Action

class BikeSafetyEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        self.speed = 0.0
        self.distance = 100.0  # Start 100m away from an obstacle
        self.steps = 0
        return Observation(speed=0.0, dist_to_obstacle=100.0, road_friction=1.0)

    def step(self, action: Action):
        self.steps += 1
        
        # 1. Physics Logic: Update speed
        # Throttle adds speed, Brake reduces it significantly
        acceleration = (action.throttle * 8.0) - (action.brake * 15.0)
        self.speed = max(0, min(self.speed + acceleration, 100)) # Limit speed 0-100
        
        # 2. Movement Logic: Update distance to obstacle
        self.distance -= (self.speed * 0.27) # Convert km/h approx to meters per step
        
        # 3. Reward Shaping (This is what the judges grade!)
        reward = 0.1  # Bonus for staying upright
        
        # Penalty for overspeeding (Safety threshold: 60km/h)
        if self.speed > 60:
            reward -= 0.5
            
        # Heavy penalty for crashing
        done = False
        if self.distance <= 0:
            reward = -10.0
            self.distance = 0
            done = True
        elif self.steps >= 100: # End of simulation
            done = True
            
        obs = Observation(
            speed=round(self.speed, 2), 
            dist_to_obstacle=round(self.distance, 2),
            road_friction=1.0
        )
        
        return obs, reward, done, {}