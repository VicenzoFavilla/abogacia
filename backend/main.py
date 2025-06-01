from fastapi import FastAPI
from backend.routers import casos, etiquetas, documento
from backend.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend Legal App")

app.include_router(casos.router)
app.include_router(etiquetas.router)
app.include_router(documento.router)


@app.get("/")
def read_root():
    return {
        "mensaje":"La api para los abogados funciona re piola"
        }