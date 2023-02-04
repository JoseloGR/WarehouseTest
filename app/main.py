import asyncio
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import product, warehouse, file
from app.schemas import ProducerMessage, ProducerResponse

app = FastAPI()

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(product.router, tags=['Products'], prefix='/api/products')
app.include_router(warehouse.router, tags=['Warehouses'], prefix='/api/warehouses')
app.include_router(file.router, tags=['Files'], prefix='/api/files')

loop = asyncio.get_event_loop()
aioproducer = AIOKafkaProducer(loop=loop, bootstrap_servers=settings.KAFKA_INSTANCE)
consumer = AIOKafkaConsumer("orders", bootstrap_servers=settings.KAFKA_INSTANCE, loop=loop)


async def consume():
    await consumer.start()
    try:
        async for msg in consumer:
            print("Consumed: ", msg.topic, msg.value)
    finally:
        await consumer.stop()


@app.on_event("startup")
async def startup_event():
    await aioproducer.start()
    loop.create_task(consume())


@app.on_event("shutdown")
async def shutdown_event():
    await aioproducer.stop()
    await consumer.stop()


@app.post("/producer/{topicname}", tags=['Producers'])
async def kafka_produce(msg: ProducerMessage, topicname: str):
    await aioproducer.send(topicname, json.dumps(msg.dict()).encode("ascii"))
    response = ProducerResponse(
        name=msg.name, message_id=msg.message_id, topic=topicname
    )
    return response


@app.get('/api/v1/healthcheck', tags=['Health'])
def health():
    return {'message': 'Hello World!'}
