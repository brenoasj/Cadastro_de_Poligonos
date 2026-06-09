"""
database.py - Módulo responsável por toda comunicação com o banco de dados PostgreSQL + PostGIS
"""

import psycopg2  # driver compatível com psycopg2-binary do requirements.txt
import json
import os       # lê variáveis de ambiente


def get_conexao():
    """Cria e retorna uma conexão com o banco PostgreSQL usando variáveis de ambiente."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ.get("DB_NAME", "poligonos_db"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "1234")
    )


def criar_tabelas():
    """Cria a extensão PostGIS e a tabela poligonos no banco."""
    with get_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS poligonos (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('escolar', 'industrial', 'residencial')),
                    geometria GEOMETRY(POLYGON, 4326) NOT NULL,
                    criado_em TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()


def inserir_poligono(nome, tipo, coordenadas):
    """Insere um novo polígono no banco e retorna o ID gerado."""
    pontos_wkt = ", ".join([f"{p[1]} {p[0]}" for p in coordenadas])

    if coordenadas[0] != coordenadas[-1]:
        pontos_wkt += f", {coordenadas[0][1]} {coordenadas[0][0]}"

    wkt = f"POLYGON(({pontos_wkt}))"

    with get_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO poligonos (nome, tipo, geometria)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id;
            """, (nome, tipo, wkt))
            novo_id = cur.fetchone()[0]
            conn.commit()
    return novo_id


def listar_poligonos():
    """Retorna todos os polígonos em formato compatível com o Leaflet."""
    with get_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, nome, tipo, ST_AsGeoJSON(geometria) as geometria_json
                FROM poligonos
                ORDER BY criado_em DESC;
            """)
            linhas = cur.fetchall()

    resultado = []
    for linha in linhas:
        geometria = json.loads(linha[3])
        coordenadas_leaflet = [
            [p[1], p[0]] for p in geometria["coordinates"][0]
        ]
        resultado.append({
            "id": linha[0],
            "nome": linha[1],
            "tipo": linha[2],
            "coordenadas": coordenadas_leaflet
        })
    return resultado


def consultar_area_por_ponto(lat, lng):
    """Retorna as áreas que contêm o ponto (lat, lng) usando ST_Contains do PostGIS."""
    with get_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, nome, tipo
                FROM poligonos
                WHERE ST_Contains(geometria, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
            """, (lng, lat))
            areas = cur.fetchall()

    return [{"id": a[0], "nome": a[1], "tipo": a[2]} for a in areas]


def deletar_poligono(id):
    """Remove um polígono do banco pelo ID."""
    with get_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM poligonos WHERE id = %s;", (id,))
            conn.commit()
