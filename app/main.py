from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import product, warehouse

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


@app.get('/api/v1/healthcheck', tags=['Health'])
def health():
    return {'message': 'Hello World!'}
