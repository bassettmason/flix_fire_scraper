from fastapi import FastAPI
from api.routes import router as api_router
# TODO: do postman tests.
app = FastAPI()

app.include_router(api_router, prefix="/api")
