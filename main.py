from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import redis
import json
from typing import Optional
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from faker import Faker
import uvicorn

app = FastAPI(title="API sobre ponto eletrônico", description="Ponto eletrônico")
fake = Faker()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = "redis://redis:6379/0"
redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

# Função para formatar a data atual
def data_atual() -> str:
    return datetime.utcnow().strftime("%d-%m-%Y")  # Data no formato 'dia-mês-ano'

# Função para converter e validar data fornecida
def parse_data(data_str: str) -> datetime:
    return datetime.strptime(data_str, "%d-%m-%Y")

# Modelo de dados para presença
class PresencaModel(BaseModel):
    usuarioId: int
    dataParaPresenca: datetime
    presenca: Optional[bool] = None
    comentario: Optional[str] = None

# Função para verificar o tipo da chave no Redis
def verificar_tipo_chave(chave: str) -> str:
    tipo = redis_client.type(chave)
    return tipo

# 1. Adicionar comentário a um aluno em um determinado dia
@app.post("/presenca/comentario")
def adicionar_comentario(presenca: PresencaModel):
    logging.info(f"Adicionando comentário para o usuário {presenca.usuarioId} na data {presenca.dataParaPresenca}")
    
    chave_usuario = str(presenca.usuarioId)
    tipo_chave = verificar_tipo_chave(chave_usuario)

    if tipo_chave != 'string':
        raise HTTPException(status_code=400, detail="Tipo de chave incorreto no Redis")

    usuario_existente = redis_client.get(chave_usuario)
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario_dados = json.loads(usuario_existente)  # Decodificando JSON armazenado
    historico = usuario_dados.get("historico", [])

    data_str = presenca.dataParaPresenca.strftime("%d-%m-%Y")
    
    # Verifica se já existe a data no histórico
    data_existente = next((item for item in historico if item["timestamp"] == data_str), None)

    if data_existente:
        data_existente["comentario"] = presenca.comentario
    else:
        novo_registro = {"timestamp": data_str, "comentario": presenca.comentario}
        historico.append(novo_registro)

    usuario_dados["historico"] = historico
    redis_client.set(chave_usuario, json.dumps(usuario_dados))  # Armazenando novamente como JSON

    return {"message": "Comentário adicionado com sucesso", "dados": presenca.dict()}

# 2. Modificar a presença de um determinado aluno
@app.put("/presenca")
def modificar_presenca(presenca: PresencaModel):
    logging.info(f"Modificando a presença do usuário {presenca.usuarioId} na data {presenca.dataParaPresenca}")

    chave_usuario = str(presenca.usuarioId)
    tipo_chave = verificar_tipo_chave(chave_usuario)

    if tipo_chave != 'string':
        raise HTTPException(status_code=400, detail="Tipo de chave incorreto no Redis")

    usuario_existente = redis_client.get(chave_usuario)
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario_dados = json.loads(usuario_existente)  # Decodificando JSON armazenado
    historico = usuario_dados.get("historico", [])

    data_str = presenca.dataParaPresenca.strftime("%d-%m-%Y")
    
    # Verifica se já existe a data no histórico
    data_existente = next((item for item in historico if item["timestamp"] == data_str), None)

    if data_existente:
        data_existente["presenca"] = presenca.presenca
        data_existente["comentario"] = presenca.comentario
    else:
        novo_registro = {
            "timestamp": data_str,
            "presenca": presenca.presenca,
            "comentario": presenca.comentario
        }
        historico.append(novo_registro)

    usuario_dados["historico"] = historico
    redis_client.set(chave_usuario, json.dumps(usuario_dados))  # Armazenando novamente como JSON

    return {"message": "Presença modificada com sucesso", "dados": presenca.dict()}

# 3. Retornar lista de presença em determinado dia
@app.get("/presenca/data")
def listar_presenca_por_data(dataParaPresenca: datetime):
    logging.info(f"Listando presenças para a data {dataParaPresenca}")

    data_str = dataParaPresenca.strftime("%d-%m-%Y")
    presencas = []

    for key in redis_client.scan_iter():
        tipo_chave = verificar_tipo_chave(key)

        if tipo_chave == 'string':
            usuario_dados = json.loads(redis_client.get(key))
            historico = usuario_dados.get("historico", [])

            for registro in historico:
                if registro["timestamp"] == data_str:
                    presencas.append({"usuarioId": key, **registro})

    return {"presencas": presencas}

# 4. Retornar a presença de uma pessoa entre duas datas
@app.get("/presenca/pessoa")
def listar_presenca_por_pessoa(usuarioId: int, dataInicial: datetime, dataFinal: datetime):
    logging.info(f"Listando presenças do usuário {usuarioId} entre {dataInicial} e {dataFinal}")

    chave_usuario = str(usuarioId)
    tipo_chave = verificar_tipo_chave(chave_usuario)

    if tipo_chave != 'string':
        raise HTTPException(status_code=400, detail="Tipo de chave incorreto no Redis")

    usuario_existente = redis_client.get(chave_usuario)
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario_dados = json.loads(usuario_existente)
    historico = usuario_dados.get("historico", [])

    data_inicial_str = dataInicial.strftime("%d-%m-%Y")
    data_final_str = dataFinal.strftime("%d-%m-%Y")

    presencas = [
        registro for registro in historico
        if data_inicial_str <= registro["timestamp"] <= data_final_str
    ]

    return {"presencas": presencas}

# 5. Endpoint para gerar usuários falsos
@app.post("/usuarios/falsos")
def gerar_usuarios_falsos(qtd: int = 1):
    logging.info(f"Gerando {qtd} usuários falsos")

    usuarios_falsos = []

    for _ in range(qtd):
        usuario_falso = {
            "usuarioId": fake.random_int(min=1000, max=9999),
            "nome": fake.name(),
        }
        usuarios_falsos.append(usuario_falso)

        # Salvando no Redis como string (JSON)
        redis_client.set(str(usuario_falso["usuarioId"]), json.dumps(usuario_falso))

    return {"usuarios_falsos": usuarios_falsos}

def on_start():
    uvicorn.run(
        app,
        host= "0.0.0.0",
        port=8000,
        log_level= "debug",
        access_log=True,
        reload=True,
    )
    
    
if __name__ == "__main__":
    on_start()
    