from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time
from collections import defaultdict

app = FastAPI()

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-o3a5il.example.com",
        "https://exam.sanand.workers.dev",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# ---------------- Rate Limiter ----------------

RATE_LIMIT = 15
WINDOW = 10

client_requests = defaultdict(list)


@app.middleware("http")
async def rate_limiter(request: Request, call_next):

    # Allow CORS preflight
    if request.method == "OPTIONS":
        return await call_next(request)

    client_id = request.headers.get("X-Client-Id")

    if client_id:
        now = time.time()

        client_requests[client_id] = [
            t for t in client_requests[client_id]
            if now - t < WINDOW
        ]

        if len(client_requests[client_id]) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )

        client_requests[client_id].append(now)

    return await call_next(request)


# ---------------- Request Context ----------------

@app.middleware("http")
async def request_context(request: Request, call_next):

    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


# ---------------- Endpoint ----------------

@app.get("/ping")
async def ping(request: Request):
    return {
        "email": "24f2001460@ds.study.iitm.ac.in",
        "request_id": request.state.request_id,
    }