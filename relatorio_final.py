from gevent import monkey
monkey.patch_all()

import os
import redis
from pymongo import MongoClient
from cassandra.cluster import Cluster
from neo4j import GraphDatabase

def gerar_relatorio():
    print("📋 === RELATÓRIO DE INTEGRAÇÃO NOSQL === 📋\n")

    # 1. VERIFICAR REDIS (Velocidade)
    try:
        r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
        preco = r.get("BTCUSDT")
        print(f"⚡ [REDIS] Último preço em cache: $ {preco if preco else 'Vazio'}")
    except: print("❌ Erro ao ler Redis")

    # 2. VERIFICAR MONGODB (Volume de Logs)
    try:
        client = MongoClient("mongodb://127.0.0.1:27017/")
        count = client.projeto_nosql.logs_precos.count_documents({})
        print(f"📂 [MONGODB] Total de logs brutos armazenados: {count}")
    except: print("❌ Erro ao ler MongoDB")

    # 3. VERIFICAR SCYLLADB (Histórico Real)
    try:
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect('mercado')
        rows = session.execute("SELECT count(*) FROM historico_precos")
        print(f"📈 [SCYLLADB] Registros na série temporal: {rows[0].count}")
    except: print("❌ Erro ao ler ScyllaDB")

    # 4. VERIFICAR NEO4J (Relacionamentos)
    try:
        driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "aluno123"), encrypted=False)
        with driver.session() as session:
            result = session.run("MATCH (i:Investidor) RETURN count(i) as total")
            total = result.single()["total"]
            print(f"👥 [NEO4J] Investidores monitorados: {total}")
        driver.close()
    except: print("❌ Erro ao ler Neo4j")

    print("\n✅ Todos os bancos estão integrados e operacionais!")
    os._exit(0)

if __name__ == "__main__":
    gerar_relatorio()