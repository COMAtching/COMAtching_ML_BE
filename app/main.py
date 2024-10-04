from app import app
from app.routes import users, recommend
from app.consumers import match_request_consumer, user_crud_consumer
import asyncio

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(match_request_consumer.consume_from_queue())
    asyncio.create_task(user_crud_consumer.consume_user_crud_request_queue())

# 라우터 등록
app.include_router(users.router)
app.include_router(recommend.router)