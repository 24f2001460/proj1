from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time
from collections import defaultdict
from fastapi.responses import JSONResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-o3a5il.example.com",
        # Yahan exam page ka origin bhi add karna hai agar assignment me diya ho.
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

RATE_LIMIT = 15
WINDOW = 10  # seconds

client_requests = defaultdict(list)
@app.middleware("http")
async def rate_limiter(request: Request, call_next):

    client_id = request.headers.get("X-Client-Id", "anonymous")

    current_time = time.time()

    # Purane timestamps hatao
    client_requests[client_id] = [
        t for t in client_requests[client_id]
        if current_time - t < WINDOW
    ]

    # Limit cross?
    if len(client_requests[client_id]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    # Current request save karo
    client_requests[client_id].append(current_time)

    response = await call_next(request)

    return response
@app.middleware("http")
async def request_context(request: Request, call_next):

    request_id = request.headers.get("X-Request-ID")

    if request_id is None:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/ping")
async def ping(request: Request):

    return {
        "email": "24f2001460@ds.study.iitm.ac.in",
        "request_id": request.state.request_id
    }