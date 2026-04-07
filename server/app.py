import uvicorn
from fastapi import FastAPI
from openenv_core.server import OpenEnvServer
# Use a direct import since we will run from inside the server folder
from environment import BikeSafetyEnv 

# 1. Create the standard FastAPI app
app = FastAPI(title="Bike Safety Environment")

# 2. Initialize the OpenEnv server wrapper
server = OpenEnvServer(env_class=BikeSafetyEnv)

# 3. Include the standard OpenEnv routes
app.include_router(server.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# 4. Define the main function for Hugging Face (Port 7860)
def main():
    """Entry point to start the server on HF port."""
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()