# Gestão de IMC

**Ferramenta simples para cálculo e categorização do IMC com visualização em gráfico.**

Este pacote permite:
- Cadastrar pessoas com dados físicos
- Atualizar registros de peso e altura ao longo do tempo
- Calcular IMC atual e histórico
- Gerar tabelas e relatórios
- Detectar inconsistências nos dados

---

## 📦 Instalação

```bash
pip install gestao-imc
```

> Substitua `gestao-imc` pelo nome real publicado no PyPI, se for diferente.

---

## 📘 Uso

```python
from gestao_imc import *
```

---

## 👥 Lista de Pessoas

Lista todas as pessoas cadastradas:

```python
listar_pessoas()
```

---

## ➕ Adicionar Pessoa

Adiciona uma nova pessoa ao sistema (cria um registro inicial com data e hora atual):

```python
add_pessoa(
    nome="Ana",
    nif="AB123456",
    idade=25,
    peso=70,
    altura=1.65,
    genero="Feminino"
)

add_pessoa(nome="Carlos", nif="CD789012", idade=30, peso=85, altura=1.75, genero="Masculino")
add_pessoa(nome="Rúben", nif="CD9023123", idade=20, peso=70, altura=1.70, genero="Masculino")
```

---

## 🕒 Adicionar Novos Dados

> **Nota:** Ao adicionar uma pessoa, o sistema registra automaticamente a data/hora da criação.  
> **Você não pode alterar os dados iniciais.**

Para registrar novas medições ao longo do tempo:

```python
add_dados(nome="Ana", nif="AB123456", peso=72, altura=1.65, data_hora="2025-04-28 08:00:00")
add_dados(nome="Ana", nif="AB123456", peso=76, altura=1.65, data_hora="2025-04-30 11:00:00")
add_dados(nome="Ana", nif="AB123456", peso=74, altura=1.65, data_hora="2025-08-06 15:30:00")
```

---

## 📊 Listagens

Listar pessoas por IMC de forma decrescente:

```python
listar_por_imc_decrescente()
```

Listar pessoas com IMC crítico (ex: abaixo ou acima dos limites saudáveis):

```python
listar_pessoas_com_imc_critico()
```

---

## 📋 Tabelas

Tabela de alturas registradas:

```python
tabela_altura()
```

Tabela de pesos registrados:

```python
tabela_peso()
```

---

## 📈 Histórico de IMC

Visualizar o histórico de IMC para uma pessoa:

```python
historico_imc(nif="AB123456")
```

Visualizar o histórico completo (atemporal):

```python
historico_imc_atemporal(nif="AB123456")
```

---

## 🛠 Testar Integridade

Verifica se há dados inconsistentes (ex: data duplicada, pessoa sem dados, etc):

```python
testar_integridade()
```

---
