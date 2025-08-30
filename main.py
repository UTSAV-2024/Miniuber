from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Mini Uber API", version="1.0.0")


class PingRequest(BaseModel):
    data: str


class PongResponse(BaseModel):
    message: str
    status: str


@app.get("/")
async def root():
    return {"message": "Welcome to Mini Uber API"}


@app.post("/ping", response_model=PongResponse)
async def ping_pong(request: PingRequest):
    if request.data == "ping":
        return PongResponse(message="pong", status="success")
    raise HTTPException(status_code=400, detail="Invalid ping data")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    # safer run config
    uvicorn.run(app, host="0.0.0.0", port=8000)
