"""
Servicio de exportación de documentos y citas jurídicas.
Equivalente a Zotero → Create Bibliography / Export.
"""
from typing import List
from io import BytesIO
from backend.models.documento import Documento
from backend.models.metadata_legal import MetadataLegal


def formatear_cita_juridica(doc: Documento) -> str:
    """
    Genera una cita en formato jurídico argentino estándar.
    Ejemplo: CSJN, "Caso Nombre", exp. 12345/2020, 15/03/2022.
    """
    m: MetadataLegal = doc.metadata_legal if doc.metadata_legal else None

    partes_str = ""
    if m and m.partes:
        actores = [p["nombre"] for p in m.partes if p.get("rol") == "actor"]
        demandados = [p["nombre"] for p in m.partes if p.get("rol") == "demandado"]
        if actores and demandados:
            partes_str = f"{', '.join(actores)} c/ {', '.join(demandados)}"

    tribunal = (m.tribunal or m.camara or "") if m else ""
    expediente = (f"Exp. {m.numero_expediente}" if m and m.numero_expediente else "")
    fecha = ""
    if m and m.fecha_resolucion:
        fecha = m.fecha_resolucion.strftime("%d/%m/%Y")

    partes = [p for p in [tribunal, partes_str, expediente, fecha] if p]
    return ", ".join(partes) or doc.nombre


def exportar_bibtex(documentos: List[Documento]) -> str:
    """Genera un archivo BibTeX con los documentos."""
    lines = []
    for doc in documentos:
        m = doc.metadata_legal
        tipo = m.tipo_documento if m else "misc"
        key = f"doc{doc.id}"
        titulo = doc.nombre.replace("{", "").replace("}", "")
        año = ""
        if m and m.fecha_resolucion:
            año = str(m.fecha_resolucion.year)
        tribunal = (m.tribunal or "") if m else ""
        expediente = (m.numero_expediente or "") if m else ""

        lines.append(f"@{tipo}{{{key},")
        lines.append(f"  title = {{{titulo}}},")
        if tribunal:
            lines.append(f"  institution = {{{tribunal}}},")
        if año:
            lines.append(f"  year = {{{año}}},")
        if expediente:
            lines.append(f"  number = {{{expediente}}},")
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def exportar_ris(documentos: List[Documento]) -> str:
    """Genera un archivo RIS (Research Information Systems) universal."""
    lines = []
    for doc in documentos:
        m = doc.metadata_legal
        tipo_map = {
            "sentencia": "CASE",
            "ley": "BILL",
            "decreto": "BILL",
            "contrato": "GEN",
            "doctrina": "JOUR",
        }
        tipo_ris = tipo_map.get(str(m.tipo_documento) if m else "", "GEN")
        lines.append(f"TY  - {tipo_ris}")
        lines.append(f"TI  - {doc.nombre}")
        if m:
            if m.tribunal:
                lines.append(f"PB  - {m.tribunal}")
            if m.fecha_resolucion:
                lines.append(f"DA  - {m.fecha_resolucion.strftime('%Y/%m/%d')}")
            if m.numero_expediente:
                lines.append(f"AN  - {m.numero_expediente}")
            if m.resumen:
                lines.append(f"AB  - {m.resumen}")
        lines.append("ER  - ")
        lines.append("")
    return "\n".join(lines)


def exportar_csv(documentos: List[Documento]) -> str:
    """Exporta lista de documentos como CSV."""
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Nombre", "Tipo", "Expediente", "Tribunal",
        "Jurisdicción", "Materia", "Fecha Resolución", "Partes"
    ])
    for doc in documentos:
        m = doc.metadata_legal
        partes_str = ""
        if m and m.partes:
            partes_str = "; ".join(f'{p.get("rol","")}: {p.get("nombre","")}' for p in m.partes)
        writer.writerow([
            doc.id,
            doc.nombre,
            str(m.tipo_documento) if m else "",
            m.numero_expediente if m else "",
            m.tribunal if m else "",
            m.jurisdiccion if m else "",
            m.materia if m else "",
            m.fecha_resolucion.strftime("%Y-%m-%d") if m and m.fecha_resolucion else "",
            partes_str,
        ])
    return output.getvalue()
