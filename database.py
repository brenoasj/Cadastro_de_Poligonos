"""
database.py - Módulo responsável por toda comunicação com o banco de dados PostgreSQL + PostGIS
"""

# psycopg (versão 3) — driver moderno, compatível com Python 3.14 no Windows
import psycopg

# Importa json para manipular dados no formato JSON
import json


def get_conexao():
    """Cria e retorna uma conexão com o banco PostgreSQL usando psycopg3."""
    return psycopg.connect(
        host="localhost",        # Endereço do servidor PostgreSQL
        port=5433,               # Porta padrão do PostgreSQL
        dbname="poligonos_db",   # Nome do banco de dados criado no pgAdmin
        user="postgres",         # Usuário do banco
        password="1234"          # Senha definida na instalação do PostgreSQL
    )


def criar_tabelas():
    """Cria a extensão PostGIS e a tabela poligonos no banco."""
    with get_conexao() as conn:           # Abre conexão (fecha automaticamente)
        with conn.cursor() as cur:        # Cria cursor SQL
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")  # Ativa PostGIS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS poligonos (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('escolar', 'industrial', 'residencial')),
                    geometria GEOMETRY(POLYGON, 4326) NOT NULL,
                    criado_em TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()  # Salva as alterações no banco


def inserir_poligono(nome, tipo, coordenadas):
    """Insere um novo polígono no banco e retorna o ID gerado."""
    # Converte lista de [lat, lng] para formato WKT exigido pelo PostGIS (lng lat)
    pontos_wkt = ", ".join([f"{p[1]} {p[0]}" for p in coordenadas])

    # Fecha o polígono se necessário (primeiro ponto == último ponto)
    if coordenadas[0] != coordenadas[-1]:
        pontos_wkt += f", {coordenadas[0][1]} {coordenadas[0][0]}"

    wkt = f"POLYGON(({pontos_wkt}))"  # Monta a string WKT completa

    with get_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO poligonos (nome, tipo, geometria)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
                RETURNING id;
            """, (nome, tipo, wkt))  # %s protege contra SQL Injection
            novo_id = cur.fetchone()[0]  # Lê o ID retornado pelo banco
            conn.commit()  # Confirma a inserção
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
            linhas = cur.fetchall()  # Recupera todos os resultados

    resultado = []
    for linha in linhas:
        geometria = json.loads(linha[3])  # Converte GeoJSON string para dicionário
        # Inverte de [lng, lat] (PostGIS) para [lat, lng] (Leaflet)
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
            # ST_MakePoint usa (lng, lat) — ordem inversa ao Leaflet
            cur.execute("""
                SELECT id, nome, tipo
                FROM poligonos
                WHERE ST_Contains(geometria, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
            """, (lng, lat))
            areas = cur.fetchall()

    # Converte tuplas para dicionários
    return [{"id": a[0], "nome": a[1], "tipo": a[2]} for a in areas]


def deletar_poligono(id):
    """Remove um polígono do banco pelo ID."""
    with get_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM poligonos WHERE id = %s;", (id,))
            conn.commit()  # Confirma a exclusão