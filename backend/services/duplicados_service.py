"""
Servicio de detección de duplicados.
Estrategia 1: Hash SHA-256 del archivo (duplicado exacto)
Estrategia 2: Número de expediente idéntico
Estrategia 3: Similitud de nombre por distancia de Levenshtein
"""
from sqlalchemy.orm import Session
from typing import List, Dict
from Levenshtein import ratio as lev_ratio

from backend.models.documento import Documento


def encontrar_duplicados_por_hash(db: Session, hash_sha256: str, excluir_id: int = None) -> List[Documento]:
    """Busca documentos con el mismo hash (archivo idéntico)."""
    q = db.query(Documento).filter(
        Documento.hash_sha256 == hash_sha256,
        Documento.hash_sha256.isnot(None)
    )
    if excluir_id:
        q = q.filter(Documento.id != excluir_id)
    return q.all()


def encontrar_duplicados_por_nombre(db: Session, nombre: str, umbral: float = 0.85) -> List[Dict]:
    """
    Busca documentos con nombre similar usando distancia de Levenshtein.
    Retorna lista de {documento, similitud}.
    """
    todos = db.query(Documento).all()
    resultado = []
    nombre_lower = nombre.lower()
    for doc in todos:
        sim = lev_ratio(nombre_lower, doc.nombre.lower())
        if sim >= umbral:
            resultado.append({"documento": doc, "similitud": round(sim, 3)})
    # Ordenar por similitud descendente
    resultado.sort(key=lambda x: x["similitud"], reverse=True)
    return resultado


def listar_grupos_duplicados(db: Session) -> List[List[Documento]]:
    """
    Agrupa todos los documentos duplicados por hash.
    Devuelve lista de grupos (cada grupo tiene 2+ docs con igual hash).
    """
    from sqlalchemy import func
    # Hashes que aparecen más de una vez
    hashes_dup = (
        db.query(Documento.hash_sha256)
        .filter(Documento.hash_sha256.isnot(None))
        .group_by(Documento.hash_sha256)
        .having(func.count(Documento.id) > 1)
        .all()
    )
    grupos = []
    for (h,) in hashes_dup:
        docs = db.query(Documento).filter(Documento.hash_sha256 == h).all()
        grupos.append(docs)
    return grupos
