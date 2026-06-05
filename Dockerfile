# Usa uma imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Impede que o Python escreva os ficheiros .pyc e garante que o output aparece no terminal logo
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala as dependências do sistema necessárias para o Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean

# Copia o requirements.txt e instala as dependências
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o resto do código do projeto
COPY . /app/