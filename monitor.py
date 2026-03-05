from gevent import monkey
monkey.patch_all()  # Essencial para o ScyllaDB no Python 3.12

import requests
import time
import redis
import os
from pymongo import MongoClient
from cassandra.cluster import Cluster
from neo4j import GraphDatabase
from datetime import datetime

# --- CONFIGURAÇÕES ---
SYMBOL = "BTCUSDT"
API_URL = f"https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}"

def setup_automatico(session_scylla, driver_neo4j):
    """Garante que as tabelas e nós existam antes do loop (Requisito do Prof)"""
    print("\n🛠️ [SETUP] Verificando estruturas nos bancos de dados...")
    
    # Setup ScyllaDB (Keyspace e Tabela de Série Temporal)
    session_scylla.execute("""
        CREATE KEYSPACE IF NOT EXISTS mercado 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """)
    session_scylla.execute("USE mercado;")
    session_scylla.execute("""
        CREATE TABLE IF NOT EXISTS historico_precos (
            moeda text, 
            horario timestamp, 
            preco float,
            PRIMARY KEY (moeda, horario)
        ) WITH CLUSTERING ORDER BY (horario DESC);
    """)
    print("✅ [SCYLLA] Keyspace e Tabela prontos.")

    # Setup Neo4j (Nós de Investidores e Relacionamentos)
    with driver_neo4j.session() as session:
        investidores = ["Alice", "Bob", "Carlos", "Diana"]
        for nome in investidores:
            session.run("""
                MERGE (i:Investidor {nome: $nome})
                MERGE (m:Moeda {simbolo: $simbolo})
                MERGE (i)-[r:ACOMPANHA]->(m)
            """, nome=nome, simbolo=SYMBOL)
    print("✅ [NEO4J] Investidores e Grafo mapeados.")

def iniciar_monitor():
    print("🚀 [SISTEMA] Iniciando Monitoramento de Mercado...")
    
    try:
        # 1. Conexões com Tratamento de Erro (Try/Except)
        r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
        
        client_mongo = MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=2000)
        db_mongo = client_mongo["projeto_nosql"]
        
        cluster_scylla = Cluster(['127.0.0.1'], connect_timeout=10)
        session_scylla = cluster_scylla.connect()
        
        driver_neo4j = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "aluno123"), encrypted=False)
        
        # Executa o Setup Inicial Automático
        setup_automatico(session_scylla, driver_neo4j)
        
    except Exception as e:
        print(f"❌ [ERRO CRÍTICO] Falha ao conectar nos bancos: {e}")
        print("Certifique-se que o docker-compose up -d foi executado.")
        return

    print(f"\n✅ Conexões estabelecidas! Monitorando {SYMBOL} a cada 5s...\n")

    while True:
        try:
            # --- FASE 1: REDIS & API (Lógica de Cache + Volatilidade) ---
            preco_antigo = r.get(SYMBOL)
            resp = requests.get(API_URL).json()
            preco_atual = float(resp['price'])
            
            # Lógica Visual de Volatilidade (DESAFIO EXTRA)
            seta = "⚪" 
            if preco_antigo:
                p_antigo = float(preco_antigo)
                if preco_atual > p_antigo: seta = "🟢 (Subiu)"
                elif preco_atual < p_antigo: seta = "🔴 (Caiu)"

            # Determina se houve Cache Hit ou Miss
            if preco_antigo and float(preco_antigo) == preco_atual:
                origem_log = "[REDIS] ⚡ Cache Hit!"
            else:
                origem_log = "[API] 🌐 Cache Miss! Fui na Binance."
                # --- FASE 2: MONGODB (Data Lake) ---
                db_mongo.logs_precos.insert_one({
                    "payload": resp, 
                    "data_coleta": datetime.now()
                })
                # Atualiza o Redis com TTL de 10s
                r.setex(SYMBOL, 10, preco_atual)

            # --- FASE 3: NEO4J (Busca de Investidores + Registro de Alerta) ---
            with driver_neo4j.session() as session:
                result = session.run("""
                    MATCH (i:Investidor)-[r:ACOMPANHA]->(m:Moeda {simbolo: $simbolo})
                    SET r.ultima_notificacao = $data
                    RETURN i.nome as nome
                """, simbolo=SYMBOL, data=datetime.now().isoformat())
                nomes_investidores = [rec["nome"] for rec in result]

            # --- FASE 4: SCYLLADB (Série Temporal) ---
            session_scylla.execute(
                "INSERT INTO historico_precos (moeda, horario, preco) VALUES (%s, %s, %s)",
                (SYMBOL, datetime.now(), preco_atual)
            )

            # --- LOG VISUAL COMPLETO (Exigência do Professor) ---
            print(f"\n--- Verificação: {SYMBOL} | {datetime.now().strftime('%H:%M:%S')} ---")
            print(f"📍 Status: {origem_log}")
            print(f"   [MONGO] 📂 Payload bruto salvo no Data Lake.")
            print(f"   [SCYLLA] 📈 Preço de ${preco_atual:,.2f} {seta} gravado na série temporal.")
            print(f"   [NEO4J] 👥 Notificando investidores: {', '.join(nomes_investidores)}")
            
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n🛑 Encerrando o monitor por comando do usuário...")
            driver_neo4j.close()
            os._exit(0)
        except Exception as e:
            print(f"⚠️ [AVISO] Ocorreu um erro no loop: {e}")
            time.sleep(2)

if __name__ == "__main__":
    iniciar_monitor()