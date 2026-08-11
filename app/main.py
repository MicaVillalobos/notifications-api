from fastapi import FastAPI

from app.routers import auth, notifications

app = FastAPI(title="Notifications API")

app.include_router(auth.router)
app.include_router(notifications.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}