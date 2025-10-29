import uvicorn
from fastapi import FastAPI, responses
from src.core.routes import routes
from src.dependencies.middlewares import AuthObjectMiddleware

app = FastAPI(
    title="Multi-Tenant Note app",
    default_response_class=responses.ORJSONResponse
)

# app.add_middleware(AuthObjectMiddleware)

@app.get("/", status_code=200)
async def index():
    return responses.RedirectResponse(url="/docs")


list(map(lambda r: app.include_router(r), routes))


def run_server():
    uvicorn.run("src.scripts.server:app", host="0.0.0.0", port=8080, reload=True)


def run_prod():
    uvicorn.run("src.scripts.server:app", host="0.0.0.0", port=8080, reload=False, workers=2)

