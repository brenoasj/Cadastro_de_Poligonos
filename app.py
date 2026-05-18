"""
app.py - Arquivo principal da aplicação Flask
Sistema de Cadastro de Polígonos por Área Geográfica
Cidade de referência: Jacareí - SP
"""

# Importa o framework Flask e utilitários para criar rotas e respostas HTTP
from flask import Flask, render_template, request, jsonify

# Importa as funções do módulo de banco de dados criado neste projeto
from database import criar_tabelas, inserir_poligono, listar_poligonos, consultar_area_por_ponto, deletar_poligono

# Importa o módulo json para serializar dados geométricos manualmente quando necessário
import json

# Cria a instância principal da aplicação Flask
# __name__ indica ao Flask onde estão os arquivos de template e static
app = Flask(__name__)


# ROTA PRINCIPAL - Carrega a página do mapa

@app.route("/")
def index():
    """
    Rota raiz da aplicação.
    Renderiza o template HTML com o mapa Leaflet.
    """
    return render_template("index.html")  # Retorna o arquivo templates/index.html


# ROTA: Cadastrar novo polígono

@app.route("/api/poligonos", methods=["POST"])
def cadastrar_poligono():
    """
    Endpoint para cadastrar um novo polígono no banco de dados.
    Recebe um JSON com nome, tipo e coordenadas do polígono.
    Método HTTP: POST
    """
    dados = request.get_json()  # Lê o corpo da requisição como JSON

    # Valida se os campos obrigatórios foram enviados na requisição
    if not dados or "nome" not in dados or "tipo" not in dados or "coordenadas" not in dados:
        # Retorna erro 400 (Bad Request) se faltar algum campo
        return jsonify({"erro": "Campos obrigatórios: nome, tipo, coordenadas"}), 400

    nome = dados["nome"]           # Nome do local/área (ex: "Fatec Jacareí")
    tipo = dados["tipo"]           # Tipo da área: 'escolar', 'industrial' ou 'residencial'
    coordenadas = dados["coordenadas"]  # Lista de pares [lat, lng] formando o polígono

    # Valida se o tipo informado é um dos valores aceitos pelo sistema
    if tipo not in ["escolar", "industrial", "residencial"]:
        return jsonify({"erro": "Tipo inválido. Use: escolar, industrial ou residencial"}), 400

    # Chama a função do banco de dados para persistir o polígono
    novo_id = inserir_poligono(nome, tipo, coordenadas)

    # Retorna sucesso com o ID gerado pelo banco
    return jsonify({"mensagem": "Polígono cadastrado com sucesso!", "id": novo_id}), 201


# ROTA: Listar todos os polígonos cadastrados

@app.route("/api/poligonos", methods=["GET"])
def obter_poligonos():
    """
    Endpoint para listar todos os polígonos salvos no banco.
    Retorna um JSON com lista de polígonos e suas coordenadas.
    Método HTTP: GET
    """
    poligonos = listar_poligonos()  # Busca todos os polígonos no banco de dados

    # Retorna a lista de polígonos como JSON para o frontend
    return jsonify(poligonos)


# ROTA: Consultar área por ponto clicado no mapa

@app.route("/api/consultar_ponto", methods=["POST"])
def consultar_ponto():
    """
    Endpoint que recebe um ponto (lat, lng) clicado no mapa
    e retorna quais áreas/polígonos contêm aquele ponto.
    Usa a função ST_Contains do PostGIS para verificação geoespacial.
    Método HTTP: POST
    """
    dados = request.get_json()  # Lê as coordenadas do ponto enviado

    # Valida se latitude e longitude foram informadas
    if not dados or "lat" not in dados or "lng" not in dados:
        return jsonify({"erro": "Informe lat e lng"}), 400

    lat = dados["lat"]  # Latitude do ponto clicado no mapa
    lng = dados["lng"]  # Longitude do ponto clicado no mapa

    # Consulta no PostGIS quais polígonos contêm o ponto informado
    areas = consultar_area_por_ponto(lat, lng)

    # Se nenhum polígono contém o ponto, informa ao usuário
    if not areas:
        return jsonify({"mensagem": "Nenhuma área encontrada para este ponto.", "areas": []})

    # Retorna as áreas encontradas com nome e tipo
    return jsonify({"areas": areas})


# ROTA: Deletar um polígono pelo ID

@app.route("/api/poligonos/<int:id>", methods=["DELETE"])
def remover_poligono(id):
    """
    Endpoint para deletar um polígono pelo seu ID.
    Método HTTP: DELETE
    """
    deletar_poligono(id)  # Chama a função de deleção no banco
    return jsonify({"mensagem": f"Polígono {id} removido com sucesso!"})


# INICIALIZAÇÃO DA APLICAÇÃO

if __name__ == "__main__":
    criar_tabelas()   # Cria as tabelas no PostgreSQL se ainda não existirem
    app.run(debug=True, host="0.0.0.0", port=5000)
    # debug=True: mostra erros detalhados (desativar em produção)
    # host="0.0.0.0": aceita conexões externas (necessário para deploy)
    # port=5000: porta padrão do Flask
