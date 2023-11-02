# Use a imagem base do Python como ponto de partida
FROM python:3.8

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos de requisitos para o contêiner e instale as dependências
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copie o código-fonte da aplicação para o contêiner
COPY . /app/

# Execute as migrações do Django


RUN python manage.py migrate

# Exponha a porta em que o servidor Django será executado (por padrão, 8000)
EXPOSE 8000

# Inicialize o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
