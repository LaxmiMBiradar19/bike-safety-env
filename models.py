from pydantic import BaseModel, Field

class Observation(BaseModel):
    speed: float = Field(..., description="Current speed of the bike in km/h")
    dist_to_obstacle: float = Field(..., description="Distance to the vehicle or object ahead in meters")
    road_friction: float = Field(default=1.0, description="1.0 for dry road, 0.6 for wet road")

class Action(BaseModel):
    throttle: float = Field(default=0.0, ge=0.0, le=1.0, description="Acceleration force (0 to 1)")
    brake: float = Field(default=0.0, ge=0.0, le=1.0, description="Braking force (0 to 1)")