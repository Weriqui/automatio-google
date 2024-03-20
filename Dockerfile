# Usar a imagem oficial do Python como imagem base
FROM python:3.9-slim

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar os arquivos de requisitos primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos da aplicação para o contêiner
COPY . .

# Informar ao Docker que a aplicação escuta na porta 5000
EXPOSE 5000

# Comando para rodar a aplicação diretamente com Python
CMD ["python", "app.py"]
