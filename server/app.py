import uvicorn
from fastapi import FastAPI
from openenv_core.server import OpenEnvServer
# Removed the dot (.) so it works inside the container
from environment import BikeSafetyEnv 

app = FastAPI(title="Bike Safety Environment")
server = OpenEnvServer(env_class=BikeSafetyEnv)
app.include_router(server.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

def main():
    # Changed port to 7860 for Hugging Face
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()