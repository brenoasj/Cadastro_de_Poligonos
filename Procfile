# Procfile — Instrui o Railway/Heroku sobre como iniciar a aplicação
# web: define o processo principal da aplicação web
# gunicorn app:app — usa o Gunicorn como servidor WSGI de produção
#   - primeiro "app" = nome do arquivo Python (app.py)
#   - segundo "app" = nome da instância Flask dentro do arquivo (app = Flask(__name__))
web: gunicorn app:app
