import uvicorn
from fastapi import (
    FastAPI,
    Request,
    WebSocket,
    WebSocketDisconnect
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
            "host_ip": "192.168.0.102",
            "port": 9000
        }
    )


@app.get("/test")
async def test():
    return "服务器收到了你的get请求"


@app.post("/test")
async def test():
    return "服务器收到了你的post请求"


@app.websocket("/test")
async def test(
        websocket: WebSocket
):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_text("服务器收到了你的websocket消息")

    except WebSocketDisconnect:
        pass


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=9500)