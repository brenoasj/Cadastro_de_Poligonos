"""
app.py - Arquivo principal da aplicação Flask
Sistema de Cadastro de Polígonos por Área Geográfica
"""

from flask import Flask, render_template, request, jsonify
from database import criar_tabelas, inserir_poligono, listar_poligonos, consultar_area_por_ponto, deletar_poligono
import json
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/poligonos", methods=["POST"])
def cadastrar_poligono():
    dados = request.get_json()

    if not dados or "nome" not in dados or "tipo" not in dados or "coordenadas" not in dados:
        return jsonify({"erro": "Campos obrigatórios: nome, tipo, coordenadas"}), 400

    nome = dados["nome"]
    tipo = dados["tipo"]
    coordenadas = dados["coordenadas"]

    if tipo not in ["escolar", "industrial", "residencial"]:
        return jsonify({"erro": "Tipo inválido. Use: escolar, industrial ou residencial"}), 400

    novo_id = inserir_poligono(nome, tipo, coordenadas)
    return jsonify({"mensagem": "Polígono cadastrado com sucesso!", "id": novo_id}), 201


@app.route("/api/poligonos", methods=["GET"])
def obter_poligonos():
    poligonos = listar_poligonos()
    return jsonify(poligonos)


@app.route("/api/consultar_ponto", methods=["POST"])
def consultar_ponto():
    dados = request.get_json()

    if not dados or "lat" not in dados or "lng" not in dados:
        return jsonify({"erro": "Informe lat e lng"}), 400

    lat = dados["lat"]
    lng = dados["lng"]

    areas = consultar_area_por_ponto(lat, lng)

    if not areas:
        return jsonify({"mensagem": "Nenhuma área encontrada para este ponto.", "areas": []})

    return jsonify({"areas": areas})


@app.route("/api/poligonos/<int:id>", methods=["DELETE"])
def remover_poligono(id):
    deletar_poligono(id)
    return jsonify({"mensagem": f"Polígono {id} removido com sucesso!"})


# Inicializa as tabelas ao subir a aplicação
with app.app_context():
    try:
        criar_tabelas()
    except Exception as e:
        print(f"Aviso: não foi possível criar tabelas na inicialização: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
