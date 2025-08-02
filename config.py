DB_SERVER   = "localhost"         # Nombre del servidor PostgreSQL
DB_NAME     = "db_personales"     # Nombre de la base de datos en Postgres
DB_USER     = "postgres"          # Usuario de Postgres
DB_PASSWORD = "72873652a"          # Contraseña de Postgres
DB_PORT     = "5432"              # Puerto por defecto de Postgres

# Cadena de conexión para psycopg2
CONNECTION_STRING = (
    f"host={DB_SERVER} "
    f"dbname={DB_NAME} "
    f"user={DB_USER} "
    f"password={DB_PASSWORD} "
    f"port={DB_PORT}"
)
