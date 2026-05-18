# 🗺️ Sistema de Polígonos por Área — Jacareí SP
**PRJ.12 — FATEC Jacareí | Matemática para Computação**

Sistema web para cadastro, visualização e consulta de polígonos geográficos categorizados como áreas **escolares**, **industriais** ou **residenciais**, com mapa interativo da cidade de Jacareí - SP.

---

## 🧱 Tecnologias Utilizadas

| Camada | Tecnologia | Função |
|---|---|---|
| Backend | Python + Flask | API REST e servidor web |
| Banco de Dados | PostgreSQL + PostGIS | Armazenamento e consulta geoespacial |
| Frontend | Leaflet.js | Mapa interativo no navegador |
| Deploy | Railway | Hospedagem gratuita na nuvem |

---

## Equipe

| Nome | GitHub | LinkedIn |
|------|--------|----------|
| Breno Augusto | [Github](https://github.com/brenoasj) | [LinkedIn](https://www.linkedin.com/in/brenoaugusto1910?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app) |
| Luka Gomes | [Github](https://github.com/LukaGomes) | [LinkedIn](https://www.linkedin.com/in/luka-gomes-12b68718a/) |

---

## 🚀 Deploy no Railway (Recomendado para entrega)

### Passo 1 — Criar conta no Railway
1. Acesse https://railway.app
2. Clique em **"Start a New Project"**
3. Faça login com sua conta do GitHub

### Passo 2 — Criar banco de dados PostgreSQL com PostGIS
1. No painel do Railway, clique em **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Aguarde o banco ser criado
3. Clique no banco → aba **"Query"**
4. Execute o comando abaixo para ativar o PostGIS:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Passo 3 — Fazer deploy da aplicação
1. Suba o projeto para um repositório no GitHub
2. No Railway, clique em **"+ New"** → **"GitHub Repo"**
3. Selecione o repositório do projeto
4. Railway detecta automaticamente que é Python e instala o `requirements.txt`

### Passo 4 — Configurar variáveis de ambiente
No painel do Railway, vá em **Variables** e adicione:

| Variável | Valor (pegar nas configurações do banco Railway) |
|---|---|
| `DB_HOST` | Host do PostgreSQL gerado pelo Railway |
| `DB_PORT` | Porta (geralmente 5433) |
| `DB_NAME` | Nome do banco |
| `DB_USER` | Usuário do banco |
| `DB_PASSWORD` | Senha do banco |

> 💡 Todas essas informações ficam na aba **"Connect"** do banco PostgreSQL no Railway.

### Passo 5 — Configurar o comando de start
No Railway, em **Settings → Deploy**, defina o comando de start:
```
gunicorn app:app
```

### Passo 6 — Acessar a aplicação
Após o deploy, Railway gera um URL público como:
```
https://seu-projeto.railway.app
```

---

## 💻 Rodar Localmente (para testes)

### Pré-requisitos
- Python 3.10+
- PostgreSQL instalado com extensão PostGIS

### Instalação do PostgreSQL + PostGIS (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

### Instalação do PostgreSQL + PostGIS (Windows)
1. Baixe o instalador em https://www.postgresql.org/download/windows/
2. Durante a instalação, marque a opção **PostGIS** no Stack Builder

### Configuração do banco local
```sql
-- Execute no psql ou pgAdmin:
CREATE DATABASE poligonos_db;
\c poligonos_db
CREATE EXTENSION postgis;
```

### Instalação das dependências Python
```bash
pip install -r requirements.txt
```

### Definir variáveis de ambiente (Linux/Mac)
```bash
export DB_HOST=localhost
export DB_PORT=5433
export DB_NAME=poligonos_db
export DB_USER=postgres
export DB_PASSWORD=sua_senha
```

### Definir variáveis de ambiente (Windows CMD)
```cmd
set DB_HOST=localhost
set DB_PORT=5433
set DB_NAME=poligonos_db
set DB_USER=postgres
set DB_PASSWORD=sua_senha
```

### Iniciar a aplicação
```bash
python app.py
```

Acesse: http://localhost:5000

---

## 📁 Estrutura do Projeto

```
projeto_poligonos/
├── app.py              # Rotas Flask (endpoints da API REST)
├── database.py         # Funções de acesso ao banco PostgreSQL + PostGIS
├── requirements.txt    # Dependências Python do projeto
├── templates/
│   └── index.html      # Frontend completo: mapa Leaflet + painel lateral
└── README.md           # Este arquivo
```

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Página principal com o mapa |
| POST | `/api/poligonos` | Cadastra novo polígono |
| GET | `/api/poligonos` | Lista todos os polígonos |
| DELETE | `/api/poligonos/<id>` | Remove um polígono pelo ID |
| POST | `/api/consultar_ponto` | Retorna as áreas que contêm um ponto (lat/lng) |

---

## 🗺️ Funcionalidades

- **Desenhar polígono** diretamente no mapa clicando nos vértices
- **Categorizar** a área como Escolar, Industrial ou Residencial
- **Visualizar** todos os polígonos cadastrados com cores por tipo
- **Clicar em qualquer ponto** do mapa e saber a qual área ele pertence
- **Múltiplas sobreposições**: um ponto pode pertencer a várias áreas
- **Deletar** áreas cadastradas pelo painel lateral

---

## 📚 Conceitos Geoespaciais Utilizados

| Conceito | Descrição |
|---|---|
| **PostGIS** | Extensão do PostgreSQL que adiciona tipos e funções geoespaciais |
| **SRID 4326** | Sistema de coordenadas WGS84 (usado por GPS e Leaflet) |
| **ST_GeomFromText** | Converte texto WKT em geometria PostGIS |
| **ST_Contains** | Verifica se um ponto está dentro de um polígono |
| **ST_AsGeoJSON** | Converte geometria PostGIS em formato GeoJSON |
| **WKT** | Well-Known Text: formato textual para geometrias (ex: `POLYGON((...))`) |
| **GeoJSON** | Formato JSON para dados geoespaciais, usado pelo Leaflet |
