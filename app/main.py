from fastapi import FastAPI

app = FastAPI()

@app.get('/api/v1/healthcheck', tags=['Health'])
def health():
    return {'message': 'Hello World!'}
