# main.py
from fastapi import FastAPI
from .routes.chain import router

# Initialize FastAPI app
app = FastAPI()

# Register the routes
app.include_router(router)

# Run the app (use uvicorn to serve this app, as shown below)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
