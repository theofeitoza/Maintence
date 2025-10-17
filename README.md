<div id="top"></div>

<div align="center">

⚙️ Maintence - Sistema de Gerenciamento de Manutenção
Uma aplicação web completa, construída com Streamlit, para otimizar e gerenciar operações de manutenção industrial.

<img alt="last-commit" src="https://img.shields.io/github/last-commit/theofeitoza/Maintence?style=flat&logo=git&logoColor=white&color=0080ff"> <img alt="repo-top-language" src="https://img.shields.io/github/languages/top/theofeitoza/Maintence?style=flat&color=0080ff">

<p><em>Tecnologias Utilizadas:</em></p> <img alt="Python" src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white"> <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white"> <img alt="SQLite" src="https://img.shields.io/badge/SQLite-003B57.svg?style=flat&logo=SQLite&logoColor=white">

</div>

📜 Índice
Visão Geral

✨ Funcionalidades

🔧 Arquitetura da Aplicação

🏁 Como Começar

Pré-requisitos

Instalação

Execução

📸 Screenshots

<hr>

🚀 Visão Geral
O projeto Maintence é um sistema de gerenciamento de manutenção (CMMS - Computerized Maintenance Management System) desenvolvido como uma aplicação web interativa. O objetivo é centralizar informações, automatizar processos e fornecer insights através de dashboards para equipes de manutenção industrial.

Construído inteiramente em Python com o framework Streamlit, o sistema oferece uma interface de usuário rica e reativa para gerenciar todos os aspectos do ciclo de vida da manutenção, desde o cadastro de equipamentos até a análise de indicadores de performance.

<hr>

✨ Funcionalidades
A plataforma conta com um conjunto robusto de módulos para uma gestão completa:

🔐 Autenticação e Gestão de Usuários: Sistema de login seguro para controlar o acesso à plataforma (login.jpg, gestao_de_usuarios.jpg).

📊 Dashboard de KPIs: Painel visual com os principais indicadores de manutenção (MTTR, MTBF, Disponibilidade) para tomada de decisão baseada em dados (kpis.jpg).

📝 Gestão de Ordens de Serviço: Crie, atribua, acompanhe e finalize ordens de serviço corretivas, preventivas e preditivas (ordem_de_servico.jpg).

🔧 Cadastro de Ativos e Equipamentos: Mantenha um registro centralizado de todos os equipamentos, suas especificações e hierarquias (equipamentos.jpg).

📦 Controle de Estoque: Gerencie peças de reposição e materiais, controlando entradas, saídas e níveis mínimos (estoque.PNG).

📈 Histórico e Monitoramento: Acesse o histórico completo de intervenções por equipamento para auditoria e análise de falhas (historico.jpg).

🧠 Predição de Falhas: Módulo para aplicar modelos de machine learning e prever a probabilidade de falhas futuras em componentes críticos (predicao.jpg).

🗺️ Mapa Interativo da Planta: Visualize a localização dos equipamentos em um mapa da planta industrial, facilitando a localização e o planejamento (mapa_planta.jpg).

<hr>

🔧 Arquitetura da Aplicação
Frontend: A interface do usuário é construída inteiramente com Streamlit, aproveitando seus componentes interativos para criar uma experiência de usuário dinâmica.

Backend e Lógica: Toda a lógica de negócios, manipulação de dados e integrações são escritas em Python.

Banco de Dados: O sistema utiliza SQLite (maintenance.db) para armazenar todos os dados de forma persistente, garantindo leveza e facilidade de implantação.

Estrutura Multi-página: O projeto utiliza a estrutura de páginas do Streamlit, com a lógica de cada módulo separada em arquivos na pasta pages/.

<hr>

🏁 Como Começar
Siga os passos abaixo para executar a aplicação em seu ambiente local.

Pré-requisitos
Python 3.8 ou superior.

Gerenciador de pacotes pip.

Instalação
Clone o repositório:

Bash

❯ git clone https://github.com/theofeitoza/Maintence.git
Navegue até o diretório do projeto:

Bash

❯ cd Maintence
Crie um ambiente virtual (recomendado):

Bash

❯ python -m venv venv
❯ source venv/bin/activate  # No Windows: venv\Scripts\activate
Instale as dependências necessárias: (Nota: Crie um arquivo requirements.txt ou instale as bibliotecas principais manualmente)

Bash

❯ pip install streamlit pandas sqlalchemy pillow
Execução
Geração de Dados (Opcional): Se for a primeira vez executando, você pode usar o script gerador_de_dados.py para popular o banco de dados com informações de exemplo.

Bash

❯ python gerador_de_dados.py
Inicie a aplicação Streamlit:

Bash

❯ streamlit run App.py
Abra seu navegador e acesse o endereço fornecido no terminal (geralmente http://localhost:8501).

<hr>

📸 Screenshots
Tela inicial do sistema

Dashboard de KPIs

<hr>

<div align="left"> <a href="#top">⬆ Voltar ao topo</a> </div>
