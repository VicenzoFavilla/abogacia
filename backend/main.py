"""
Backend Legal — Gestor de documentos jurídicos estilo Zotero.
Levantá con: uvicorn backend.main:app --reload
Swagger UI: http://localhost:8000/docs
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import traceback

from backend.database import Base, engine

# ── Importar TODOS los modelos antes de create_all ──────────────────────────
from backend.models import (  # noqa: F401
    caso, documento, etiqueta, anotacion, doc_etiqueta,
    usuario, coleccion, metadata_legal, revision, nota,
    relacion_documento, feed
)
from backend.models.usuario import Usuario
from backend.services.auth_service import hash_password
from sqlalchemy.orm import Session
from backend.database import SessionLocal

# ── Routers ──────────────────────────────────────────────────────────────────
from backend.routers import (
    auth, casos, etiquetas, documento as documento_router,
    anotacion as anotacion_router, colecciones, editor, busqueda,
    notas, duplicados, exportacion, feeds
)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# ── Crear carpeta de uploads ──────────────────────────────────────────────────
os.makedirs("uploads", exist_ok=True)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Backend Legal — Gestor Jurídico estilo Zotero",
    description="""
API completa para gestión de documentos legales.

## Funcionalidades principales
- 📁 **Colecciones** jerárquicas (equivalente a Zotero Collections)
- 📄 **Editor de documentos** con auto-guardado (Word, PDF, TXT)
- 🔍 **Búsqueda** full-text y avanzada por tribunal, materia, dates
- 🏷️ **Etiquetas** y metadatos legales ricos
- 📝 **Notas** rich text ligadas a documentos/casos
- 🔗 **Relaciones** entre documentos (cita, deroga, modifica)
- 👥 **Duplicados** — detección y fusión
- 📤 **Exportación** — citas jurídicas, BibTeX, RIS, CSV
- 📡 **Feeds** — RSS del Boletín Oficial y Infoleg
- 🔐 **Autenticación** JWT
""",
    version="2.0.0",
)

# CORS — para Flutter web y desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "traceback": traceback.format_exc()}
    )

# ── Registrar Routers ─────────────────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    db: Session = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.email == "admin@abogacia.com").first()
        if not admin:
            nuevo_admin = Usuario(
                nombre="Administrador",
                email="admin@abogacia.com",
                hashed_password=hash_password("admin"),
                es_admin=True,
                activo=True
            )
            db.add(nuevo_admin)
            db.commit()
            print("✅ Creado usuario admin por defecto (admin@abogacia.com / admin)")
    finally:
        db.close()

app.include_router(auth.router)
app.include_router(casos.router)
app.include_router(etiquetas.router)
app.include_router(documento_router.router)
app.include_router(anotacion_router.router)
app.include_router(colecciones.router)
app.include_router(editor.router)
app.include_router(busqueda.router)
app.include_router(notas.router)
app.include_router(duplicados.router)
app.include_router(exportacion.router)
app.include_router(feeds.router)


@app.get("/", tags=["Estado"])
def health_check():
    return {
        "estado": "✅ Backend Legal activo",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "casos": "/casos",
            "documentos": "/documentos",
            "colecciones": "/colecciones",
            "editor": "/documentos/{id}/contenido",
            "busqueda": "/buscar",
            "notas": "/notas",
            "etiquetas": "/etiquetas",
            "exportacion": "/exportar",
            "feeds": "/feeds",
            "duplicados": "/duplicados",
        }
    }