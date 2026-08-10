from fastapi import FastAPI

from app.routers import health, illustrations, characters

app = FastAPI(title="IMAGE_BE")

app.include_router(health.router)
app.include_router(illustrations.router)
app.include_router(characters.router)

@app.get("/")
def read_root():
    return {"Hello": "Secret Backend Project"}
