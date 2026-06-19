FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instala as dependências necessárias do sistema
RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean

# Copia e instala as dependências a partir do ficheiro correto
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia a árvore inteira do projeto para dentro do container
COPY . /app/

# Garante que o Docker entra na pasta do código antes de compilar
WORKDIR /app/software

# Força o Django a recolher os ficheiros estáticos da pasta software/static
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput
RUN python manage.py seeder

EXPOSE 8520

# Executa o servidor através do gunicorn em modo assíncrono seguro
CMD ["gunicorn", "configuracao.wsgi:application", "--bind", "0.0.0.0:8520"]