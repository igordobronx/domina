#imagem base oficial do python
FROM python:3.12-slim

#define o diretorio do trabalho dentro do container
WORKDIR /app

#copia e instala as dependencias (aproveita o cache de camadas do docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copia todo o restante do codigo da aplicação
COPY . .

# documenta a porta em que o container escuta
EXPOSE 8000

#comando para iniciar o servidor Uvicorn escutando em 0,0,0,0
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]