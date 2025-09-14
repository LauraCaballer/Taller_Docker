from fastapi import FastAPI, Request, HTTPException
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()
DATA_FILE = "/data/notas.txt"

# Configuración de la base de datos desde variables de entorno
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# Conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME,
        cursor_factory=RealDictCursor
    )

# Crear tabla si no existe
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id SERIAL PRIMARY KEY,
            contenido TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()  # Ejecutar al iniciar

# Ruta para guardar nota
@app.post("/nota")
async def guardar_nota(request: Request):
    nota = (await request.body()).decode()
    
    # Guardar en archivo
    with open(DATA_FILE, "a") as f:
        f.write(nota + "\n")
    
    # Guardar en base de datos
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notas (contenido) VALUES (%s)", (nota,))
    conn.commit()
    cur.close()
    conn.close()
    
    return {"mensaje": "Nota guardada"}

# Ruta para leer notas desde archivo
@app.get("/")
def leer_notas():
    if not os.path.exists(DATA_FILE):
        return {"notas": []}
    with open(DATA_FILE, "r") as f:
        return {"notas": f.read().splitlines()}

# Ruta para contar notas
@app.get("/conteo")
def contar_notas():
    if not os.path.exists(DATA_FILE):
        return {"conteo": 0}
    with open(DATA_FILE, "r") as f:
        lineas = f.readlines()
        return {"conteo": len(lineas)}

# Ruta para obtener el autor desde variable de entorno
@app.get("/autor")
def leer_autor():
    autor = os.getenv("AUTOR", "Desconocido")
    return {"autor": autor}

# Ruta para leer notas desde la base de datos
@app.get("/notas-db")
def leer_notas_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notas")
    notas = cur.fetchall()
    cur.close()
    conn.close()
    return {"notas_db": notas}