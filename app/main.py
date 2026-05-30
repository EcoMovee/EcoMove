from fastapi import FastAPI
from api.v1.usuario_router import router

app = FastAPI(title="EcoMove API", version="1.0.0")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "EcoMove API funcionando"}