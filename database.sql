CREATE DATABASE IF NOT EXISTS Exibit;

USE Exibit;

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    contraseña TEXT NOT NULL,
    rol TEXT DEFAULT 'abogado' -- admin, abogado, asistente, etc.
);

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT,
    dni_cuit TEXT,
    telefono TEXT,
    email TEXT,
    direccion TEXT
);

CREATE TABLE casos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    tipo TEXT, -- Ej: “Laboral”, “Civil”, “Penal”
    estado TEXT, -- “Activo”, “Archivado”, “Cerrado”
    fecha_inicio TEXT,
    fecha_cierre TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caso_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    tipo TEXT, -- “Demanda”, “Prueba”, “Dictamen”, etc.
    ruta_archivo TEXT NOT NULL, -- Ubicación del PDF, Word, etc.
    fecha_subida TEXT,
    version INTEGER DEFAULT 1,
    descripcion TEXT,
    FOREIGN KEY (caso_id) REFERENCES casos(id)
);

CREATE TABLE etiquetas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
);

CREATE TABLE documento_etiqueta (
    documento_id INTEGER NOT NULL,
    etiqueta_id INTEGER NOT NULL,
    PRIMARY KEY (documento_id, etiqueta_id),
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE,
    FOREIGN KEY (etiqueta_id) REFERENCES etiquetas(id) ON DELETE CASCADE
);

CREATE TABLE anotaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    fecha TEXT,
    autor TEXT,
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE
);
