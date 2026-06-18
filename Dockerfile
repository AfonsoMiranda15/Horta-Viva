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

# Como o Django está dentro da pasta software/, mudamos o WORKDIR para lá
WORKDIR /app/software

# Expõe a porta de desenvolvimento desejada
EXPOSE 8520

# Comando padrão que o Render vai executar ao iniciar o container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8520"]