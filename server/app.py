import uvicorn
from fastapi import FastAPI
from openenv.server import OpenEnvServer
from .environment import BikeSafetyEnv

# 1. Create the standard FastAPI app
app = FastAPI(title="Bike Safety Environment")

# 2. Initialize the OpenEnv server wrapper
server = OpenEnvServer(env_class=BikeSafetyEnv)

# 3. Include the standard OpenEnv routes
app.include_router(server.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# 4. Define the main function that OpenEnv is looking for
def main():
    """Entry point for the OpenEnv CLI to start the server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 5. Add the standard Python entry point
if __name__ == "__main__":
    main()