from fastapi import FastAPI

from app.routers import health

app = FastAPI(title="IMAGE_BE")

app.include_router(health.router)


@app.get("/")
def read_root():
    return {"Hello": "Secret Backend Project"}
