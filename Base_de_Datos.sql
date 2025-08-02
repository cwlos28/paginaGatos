-- ================================
-- 1) Crear la base de datos y conectarse
--    (en psql:)
--      CREATE DATABASE db_personales;
--      \c db_personales
-- ================================

-- -------------------------------
-- 2) Tabla de login (único usuario)
-- -------------------------------
CREATE TABLE login (
    id           BIGSERIAL PRIMARY KEY,
    username     VARCHAR(50) NOT NULL UNIQUE,
    contraseña   VARCHAR(255) NOT NULL
);

-- -------------------------------
-- 3) Tabla de categorías
-- -------------------------------
CREATE TABLE categorias (
    id          BIGSERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);

-- -------------------------------
-- 4) Tabla de etiquetas
-- -------------------------------
CREATE TABLE etiquetas (
    id     BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- -------------------------------
-- 5) Tabla de gastos
-- -------------------------------
CREATE TABLE gastos (
    id            BIGSERIAL PRIMARY KEY,
    id_categoria  BIGINT       REFERENCES categorias(id)  ON DELETE SET NULL,
    descripcion   VARCHAR(255),
    monto         NUMERIC(10,2) NOT NULL CHECK (monto >= 0),
    fecha         DATE         NOT NULL DEFAULT CURRENT_DATE
);

-- -------------------------------
-- 6) Tabla de ingresos
-- -------------------------------
CREATE TABLE ingresos (
    id           BIGSERIAL PRIMARY KEY,
    descripcion  VARCHAR(255),
    monto        NUMERIC(10,2) NOT NULL CHECK (monto >= 0),
    fecha        DATE         NOT NULL DEFAULT CURRENT_DATE
);

-- -------------------------------
-- 7) Tabla de presupuestos
-- -------------------------------
CREATE TABLE presupuestos (
    id            BIGSERIAL PRIMARY KEY,
    id_categoria  BIGINT       NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
    monto_limite  NUMERIC(10,2) NOT NULL CHECK (monto_limite >= 0),
    mes           INTEGER      NOT NULL CHECK (mes BETWEEN 1 AND 12),
    anio          INTEGER      NOT NULL CHECK (anio >= 2000)
);

-- -------------------------------
-- 8) Tabla intermedia gasto–etiqueta
-- -------------------------------
CREATE TABLE gasto_etiqueta (
    id_gasto    BIGINT NOT NULL REFERENCES gastos(id)     ON DELETE CASCADE,
    id_etiqueta BIGINT NOT NULL REFERENCES etiquetas(id)  ON DELETE CASCADE,
    PRIMARY KEY (id_gasto, id_etiqueta)
);

-- -------------------------------
-- 9) Tabla de archivos adjuntos
-- -------------------------------
CREATE TABLE archivos (
    id             BIGSERIAL PRIMARY KEY,
    id_gasto       BIGINT       NOT NULL REFERENCES gastos(id)    ON DELETE CASCADE,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo   VARCHAR(255) NOT NULL
);
