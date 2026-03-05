# 🚀 Fintech NoSQL - Monitoramento de Cotações em Tempo Real

  

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Docker](https://img.shields.io/badge/Docker-Containers-blue)
![Redis](https://img.shields.io/badge/Redis-Cache-red)
![MongoDB](https://img.shields.io/badge/MongoDB-Data%20Lake-green)
![ScyllaDB](https://img.shields.io/badge/ScyllaDB-Time%20Series-orange)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20Database-purple)  

Este projeto foi desenvolvido como trabalho final da disciplina de **Bancos de Dados NoSQL**.

O objetivo é orquestrar diferentes tecnologias NoSQL para **monitorar cotações de criptomoedas da Binance em tempo real**, utilizando o conceito de **persistência poliglota**.

---  

## 🧠 Arquitetura do Sistema

 ```mermaid

flowchart LR  
  
subgraph Data_Source  
A[Binance API]  
end  
  
subgraph Application  
B[Python Monitor Script]  
end  
  
subgraph Databases  
C[Redis Cache]  
D[MongoDB Data Lake]  
E[ScyllaDB Time Series]  
F[Neo4j Graph Database]  
end  
  
subgraph Usage  
G[Consulta rápida de preços]  
H[Auditoria e logs]  
I[Histórico de cotações]  
J[Sistema de alertas]  
end  
  
A --> B  
  
B --> C  
B --> D  
B --> E  
B --> F  
  
C --> G  
D --> H  
E --> I  
F --> J
```

O sistema coleta cotações da API da Binance e distribui os dados entre diferentes bancos NoSQL, cada um especializado em um tipo de problema.

### 🛠️ Tecnologias Utilizadas

| Banco | Tipo | Função no Sistema |
|------|------|------|
| Redis | Key-Value | Cache de cotações |
| MongoDB | Document Store | Armazenamento de logs |
| ScyllaDB | Wide Column | Histórico de preços |
| Neo4j | Graph Database | Rede de investidores |


Essa abordagem permite usar o banco certo para o problema certo.

  
## 🚀 Como Executar

### 1. Pré-requisitos
-   Docker    
-   Docker Compose    
-   Python 3.12
### 2. Subir os bancos de dados
Na raiz do projeto execute:  
```
docker-compose up -d
```
Aguarde aproximadamente 40 segundos para que todos os bancos estejam prontos.

### 3. Criar ambiente virtual Python
```
python -m venv venv
```

#### Ativar ambiente
##### Windows
```
.\venv\Scripts\activate
```
##### Linux ou Mac
```
source venv/bin/activate
```
##### Instalar dependências
``` 
pip install -r requirements.txt
```

### 4. Iniciar o monitoramento 
O script realiza o setup dos bancos e inicia o loop de coleta.
```
python monitor.py
```

### 5. Gerar relatório rápido
Para validar os dados gravados em cada banco:
```
python relatorio_final.py
```
## 📂 Estrutura do Projeto
```
├── monitor.py                # Script principal que coleta dados da Binance
├── relatorio_final.py        # Script para validar dados armazenados
├── requirements.txt          # Dependências Python do projeto
├── docker-compose.yml        # Containers dos bancos NoSQL
├── README.md                 # Documentação do projeto
```

## 📊 Estrutura da Persistência Poliglota
| Tipo de dado | Banco escolhido | Motivo |
|---|---|---|
| Cache de preço | Redis | Latência extremamente baixa |
| Log bruto da API | MongoDB | Estrutura flexível JSON |
| Histórico de preço | ScyllaDB | Escrita massiva e escalabilidade |
| Relação entre investidores | Neo4j | Consulta eficiente de grafos |

## 🎓 FAQ – Defesa Técnica
- **Por que o Redis pode aparecer vazio?**
O Redis utiliza TTL de 10 segundos. Isso garante que o investidor sempre veja preços atualizados e reduz chamadas à API.
---
- **Por que usar ScyllaDB em vez de SQL?**
Séries temporais geram milhões de registros rapidamente. O ScyllaDB, baseado em Cassandra, utiliza LSM-Tree, permitindo escrita extremamente rápida e escalabilidade horizontal.
---
- **Por que salvar os dados brutos no MongoDB?**
Seguimos o conceito de Data Lake. O dado original é salvo sem transformação, permitindo reprocessamento futuro caso a regra de negócio mude.
---
- **Como o Neo4j ajuda no sistema de alertas?**
O Neo4j permite percorrer relações entre investidores e ativos diretamente no grafo, evitando joins complexos e mantendo consultas rápidas mesmo com grande volume de usuários.
--- 

# 👨‍💻 Autor

THIERRY PEREIRA CANOCO