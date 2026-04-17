import uvicorn
from fastapi import (
    FastAPI,
    Request
)
from fastapi.responses import (
    HTMLResponse
)
from fastapi.middleware.cors import (
    CORSMiddleware
)
from fastapi.staticfiles import (
    StaticFiles
)
from fastapi.templating import (
    Jinja2Templates
)
from contextlib import (
    asynccontextmanager
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.templates = Jinja2Templates(directory="./web")
    app.mount("/web", StaticFiles(directory="./web"), name="web")

    yield


app = FastAPI(
    title="mini server",
    docs_url="/docs",
    description="",
    version="0.0.1",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return request.app.templates.TemplateResponse(
        request, "index.html",
        context={
            "title": "mini server",
        }
    )


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=9000)