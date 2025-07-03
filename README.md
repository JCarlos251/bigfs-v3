
# 🗂️ Sistema de Arquivos Distribuídos com Python e Pyro5

Este projeto implementa um **sistema de arquivos distribuídos** simples utilizando a linguagem **Python** e a biblioteca **Pyro5** para comunicação remota entre processos distribuídos. Disciplina de Sistemas Distribuídos - UFG, 2025/1

Para informações, acesse os arquivos:

Apresentação: Arquitetura BigFSv3 - apresentação.pdf

Artigo BigFS.pdf

---

## 📦 Bibliotecas Necessárias

```
Pyro5
msgpack
```


## 🚀 Como Executar (Windows)

Você pode executar tudo de forma automática ou manual.

### 🔁 Execução Automática

Execute o script de inicialização de todos os serviços:

```bash
script/server/StartAllServices
```

Em seguida, inicie o cliente com:

```bash
script/client/start_client
```

---

### 🧩 Execução Manual

Caso queira executar os serviços um por um, abra **6 terminais** diferentes e execute os comandos na seguinte ordem:

```bash
python -m Pyro5.nameserver
python -m namenode.main_namenode
python -m datanode.main1
python -m datanode.main2
python -m datanode.main3
python -m datanode.main4
python -m cliente.main_cliente
```

---

## 🌐 Executando em Máquinas Diferentes (Rede)

Para executar os serviços em diferentes máquinas (modo distribuído real):

1. Identifique o **IP da máquina que irá rodar o Pyro5 NameServer** (exemplo: `192.168.0.10`).
2. Edite os arquivos `cliente/main_cliente.py` e `datanode/mainX.py` onde houver:

```python
ns = Pyro5.api.locate_ns()
```

E substitua por:

```python
ns = Pyro5.api.locate_ns(host="192.168.0.10")
```

3. Certifique-se de que:
   - Todas as máquinas estão na mesma rede.
   - O firewall permite conexões na porta usada pelo NameServer (padrão: `9090`).
   - O Python esteja instalado em todas as máquinas com as bibliotecas necessárias.

---


## 🏗️ Arquitetura

### 🧠 NameNode
- Responsável por manter **metadados** e informações sobre os blocos dos arquivos.
- Gerencia a **divisão dos arquivos em chunks** (partes menores).
- Controla a criação de **réplicas** para garantir a redundância dos dados.

### 🗃️ DataNodes
- Armazenam fisicamente os **blocos reais dos arquivos**.
- Respondem ao NameNode com informações de status (heartbeat).

### 👤 Cliente
- Se conecta ao **NameNode** para obter informações sobre onde e como acessar os arquivos.
- Realiza operações como:
  - `ls` (listar arquivos)
  - `upload` (envio de arquivos)
  - `download` (obtenção de arquivos)
  - `delete` (remoção de arquivos)

---

## ✅ Requisitos Funcionais

-  **Upload** e **armazenamento** de arquivos em nós distribuídos.
-  **Download** de arquivos completos a partir dos blocos armazenados.
-  **Listagem** dos arquivos existentes no sistema.
-  **Deleção** de arquivos, removendo metadados e blocos associados.

---

## ⚙️ Requisitos Não Funcionais

-  **Replicação** automática de blocos para tolerância a falhas.
-  **Desempenho** otimizado para acesso e escrita de dados.
-  **Tolerância a Falhas**, mantendo o sistema funcionando mesmo com falhas em DataNodes.
-  **Data Sharding**, separando os dados em múltiplos nós para escalabilidade.
-  **Balanceamento de Carga**, distribuindo blocos de forma equilibrada entre os DataNodes.



