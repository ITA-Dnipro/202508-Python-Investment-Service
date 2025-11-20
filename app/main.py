from fastapi import FastAPI
from app.routers.requests import router as requests_router

app = FastAPI(title="Investment Service", version="0.1.0", redirect_slashes=False)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(requests_router)
