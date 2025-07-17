#  Projeto de Bases de Dados — Contratos Públicos 2024

##  Descrição

Este projeto foi desenvolvido no âmbito da unidade curricular de Bases de Dados (CC2005) e tem como objetivo a criação de uma base de dados relacional, baseada em contratos públicos realizados nos primeiros meses de 2024. O projeto inclui:

- Modelação UML
- Conversão para modelo relacional
- Povoamento da base de dados
- Consultas SQL relevantes
- Desenvolvimento de uma aplicação web em Python (Flask) para interação com os dados

---

##  Dados e Universo Considerado

- Fonte: Contratos Públicos 2024 (ficheiro Excel)
- Período: 2023-12-01 a 2024-02-28
- Registos: 21 748 contratos
- Envolvimento internacional: 17 países
- Campos disponíveis: 15 por contrato (ex: tipo de contrato, procedimento, cliente, vendedor, valor, localização, etc.)

---

## 🌐 Aplicação Web

Uma aplicação **Flask** foi desenvolvida para consultar e visualizar os dados. Endpoints disponíveis:

- `/` — Página inicial
- `/contratos/` — Lista de contratos
- `/vendedores/`, `/clientes/`, `/pais/` — Listagens de entidades
- `/pais/<id>/` — Lista distritos do país
- `/pais/distritos/<id>/` — Lista municípios do distrito
- `/perguntas/<n>/` — Consulta SQL n (1 a 16)

--- 

## Tecnologias Utilizadas

- **Python 3.10.12**
- Bibliotecas:
   - `pygame 2.6.1`
   - `numpy 2.2.3`
   - `scikit-learn 1.6.1`
   - `matplotlib 3.10.0`
   - `pandas 2.2.3`
   - `joblib 1.4.2`

---

## Como Executar
cd app

python server.py

http://127.0.0.1:5000/
