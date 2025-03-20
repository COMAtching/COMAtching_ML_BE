from app import app
from app.routes import users, recommend
from app.consumers import match_request_consumer, user_crud_consumer
import asyncio

@app.on_event("startup")
async def startup_event():
    print("Starting up FastAPI application...")
    try:
        asyncio.create_task(match_request_consumer.consume_from_match_request_queue())
        asyncio.create_task(user_crud_consumer.consume_user_crud_request_queue())
        print("Consumers started successfully.")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise e

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# 라우터 등록
app.include_router(users.router)
app.include_router(recommend.router)
