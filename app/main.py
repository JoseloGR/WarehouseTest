import asyncio
import pandas as pd

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI, UploadFile, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import get_db
from app import models
from app.routers import product, warehouse
from app.utils import serializer, deserializer

AUTO_IMPORT = False

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

loop = asyncio.get_event_loop()
aioproducer = AIOKafkaProducer(
    loop=loop,
    bootstrap_servers=settings.KAFKA_INSTANCE,
    enable_idempotence=True,
    value_serializer=serializer,
    compression_type="gzip")
consumer = AIOKafkaConsumer(settings.KAFKA_TOPIC_ORDERS,
    bootstrap_servers=settings.KAFKA_INSTANCE,
    loop=loop,
    value_deserializer=deserializer)


@app.on_event("startup")
async def startup_event():
    await aioproducer.start()
    loop.create_task(consume())


@app.on_event("shutdown")
async def shutdown_event():
    await aioproducer.stop()
    await consumer.stop()


@app.post('/api/files/excel', tags=['Files'])
async def upload_file(file: UploadFile):
    try:    
        contents = await file.read()
        excel_data = pd.read_excel(contents)
        excel_data.fillna(value=0, inplace=True)
        list_data = excel_data.to_dict(orient='records')
        
        for order in list_data:
            filtered_dict = dict(filter(lambda elem: elem[1] != 0 or type(elem[1]) == str, order.items()))
            if filtered_dict.get('Sub inventario'):
                # sending messages
                await aioproducer.send(settings.KAFKA_TOPIC_ORDERS, filtered_dict)
        
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))


async def consume():
    await consumer.start()
    _db = next(get_db())
    try:
        async for msg in consumer:
            print("Consumed: ", msg.topic, msg.value)

            # warehouse ref
            warehouse = _db.query(models.Warehouse).filter(models.Warehouse.sub_inventory == msg.value.get('Sub inventario')).first()
            if not warehouse:
                print(f"Orden de compra no puede ser procesada para {str(msg.value)}")
                if AUTO_IMPORT:
                    new_warehouse = models.Warehouse(**{'sub_inventory': msg.value.get('Sub inventario'), 'name': msg.value.get('PDV')})
                    _db.add(new_warehouse)
                    _db.commit()
                    _db.refresh(new_warehouse)
                    warehouse = new_warehouse

            if warehouse:
                exists_order = _db.query(models.Order).filter(models.Order.warehouse_id == warehouse.id).first()
                if not exists_order:
                    new_order = models.Order(total_units=msg.value.get('TOTAL'), warehouse_id=warehouse.id)
                    _db.add(new_order)

                    for key, value in msg.value.items():
                        if key not in ['Sub inventario', 'PDV', 'TOTAL']:
                            _product_db = _db.query(models.Product).filter(models.Product.sku == key).first()
                            if AUTO_IMPORT and not _product_db:
                                new_product = models.Product(**{'sku': key})
                                _db.add(new_product)
                                _db.commit()
                                _db.refresh(new_product)
                                _product_db = new_product

                            if _product_db:
                                new_order_detail = models.OrderDetail(
                                    order = new_order,
                                    product = _product_db,
                                    quantity = value
                                )
                                _db.add(new_order_detail)
                    _db.commit()

    finally:
        await consumer.stop()


@app.get('/api/v1/healthcheck', tags=['Health'])
def health():
    return {'message': 'Hello World!'}
