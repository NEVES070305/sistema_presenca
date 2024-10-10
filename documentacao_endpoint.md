# Documentação de Endpoints da API de Presença

## 1. `/presenca/comentario` (POST)
- **Descrição**: Adiciona um comentário para um aluno em um determinado dia.
- **Parâmetros**:
  - `dataParaPresenca` (DateTime): Data para a qual o comentário será adicionado.
  - `usuarioId` (int): Identificador do usuário/aluno.
  - `comentario` (string): Comentário a ser adicionado.
- **Resposta**:
  - Mensagem de confirmação e os dados da presença com o comentário.

## 2. `/presenca` (PUT)
- **Descrição**: Modifica a presença de um aluno em um determinado dia.
- **Parâmetros**:
  - `dataParaPresenca` (DateTime): Data para a qual a presença será modificada.
  - `usuarioId` (int): Identificador do usuário/aluno.
  - `presenca` (boolean, opcional): Indica se o aluno esteve presente (true) ou ausente (false).
  - `comentario` (string, opcional): Comentário adicional sobre a presença.
- **Resposta**:
  - Mensagem de confirmação e os dados atualizados da presença.

## 3. `/presenca/data` (GET)
- **Descrição**: Retorna uma lista de presenças em uma determinada data.
- **Parâmetros**:
  - `dataParaPresenca` (DateTime): Data para a qual se deseja obter a lista de presenças.
- **Resposta**:
  - Lista de alunos com suas presenças e comentários registrados na data especificada.

## 4. `/presenca/pessoa` (GET)
- **Descrição**: Retorna a presença de um aluno em um intervalo de datas.
- **Parâmetros**:
  - `usuarioId` (int): Identificador do usuário/aluno.
  - `dataInicial` (DateTime): Data inicial do período de busca.
  - `dataFinal` (DateTime): Data final do período de busca.
- **Resposta**:
  - Lista de registros de presença do aluno no período especificado.

## 5. `/usuarios/falsos` (POST)
- **Descrição**: Gera usuários fictícios para teste.
- **Parâmetros**:
  - `qtd` (int, opcional): Quantidade de usuários falsos a serem gerados. Valor padrão: 1.
- **Resposta**:
  - Lista de usuários falsos gerados com `usuarioId` e `nome`.

# Observações Gerais
- Todos os parâmetros do tipo `DateTime` devem estar no formato `"dd-mm-aaaa"`.
- Em caso de erros, como usuário não encontrado ou tipo de chave incorreto no Redis, será retornado um código de erro apropriado (ex.: 400 ou 404).
- A API faz uso do Redis para armazenar e recuperar os registros de presença e comentários dos alunos.

# Docker Compose e Dockerfile

## Docker Compose
```yaml
docker-compose version: '3.9'

services:  
  redis:
    image: redis
    ports:
      - "6380:6379"
    deploy:
      resources:
        limits:
          cpus: '0.75'
          memory: '1.5GB'

  storage_app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: '0.5GB'
```

## Dockerfile
```dockerfile
# Use uma imagem base Python oficial
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o container
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Define o comando padrão para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
