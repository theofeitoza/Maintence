<div id="top"></div>

<div align="center">

# ⚙️ Maintence - Sistema de Gerenciamento de Manutenção
*Uma aplicação web completa, construída com Streamlit, para otimizar e gerenciar operações de manutenção industrial.*

<br>

<img alt="last-commit" src="https://img.shields.io/github/last-commit/theofeitoza/maintence?style=flat&logo=git&logoColor=white&color=0080ff">
<img alt="repo-top-language" src="https://img.shields.io/github/languages/top/theofeitoza/maintence?style=flat&color=0080ff">

<p><em>Tecnologias Utilizadas:</em></p>
<img alt="Python" src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white">
<img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white">
<img alt="SQLite" src="https://img.shields.io/badge/SQLite-003B57.svg?style=flat&logo=SQLite&logoColor=white">

</div>

---

## 📜 Índice
- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura da Aplicação](#-arquitetura-da-aplicação)
- [Como Começar](#-como-começar)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação](#instalação)
  - [Execução](#execução)
- [Screenshots](#-screenshots)

---

## 🚀 Visão Geral
O projeto **Maintence** é um sistema de gerenciamento de manutenção (CMMS - Computerized Maintenance Management System) desenvolvido como uma aplicação web interativa. O objetivo é centralizar informações, automatizar processos e fornecer insights através de dashboards para equipes de manutenção industrial.

Construído inteiramente em Python com o framework Streamlit, o sistema oferece uma interface de usuário rica e reativa para gerenciar todos os aspectos do ciclo de vida da manutenção, desde o cadastro de equipamentos até a análise de indicadores de performance.

---

## ✨ Funcionalidades
A plataforma conta com um conjunto robusto de módulos para uma gestão completa:

-   **🔐 Autenticação e Gestão de Usuários:** Sistema de login seguro para controlar o acesso à plataforma.
-   **📊 Dashboard de KPIs:** Painel visual com os principais indicadores de manutenção (MTTR, MTBF, Disponibilidade) para tomada de decisão baseada em dados.
-   **📝 Gestão de Ordens de Serviço:** Crie, atribua, acompanhe e finalize ordens de serviço corretivas, preventivas e preditivas.
-   **🔧 Cadastro de Ativos e Equipamentos:** Mantenha um registro centralizado de todos os equipamentos, suas especificações e hierarquias.
-   **📦 Controle de Estoque:** Gerencie peças de reposição e materiais, controlando entradas, saídas e níveis mínimos.
-   **📈 Histórico e Monitoramento:** Acesse o histórico completo de intervenções por equipamento para auditoria e análise de falhas.
-   **🧠 Predição de Falhas:** Módulo para aplicar modelos de machine learning e prever a probabilidade de falhas futuras em componentes críticos.
-   **🗺️ Mapa Interativo da Planta:** Visualize a localização dos equipamentos em um mapa da planta industrial, facilitando a localização e o planejamento.

---

## 🔧 Arquitetura da Aplicação
-   **Frontend:** A interface do usuário é construída inteiramente com Streamlit, aproveitando seus componentes interativos para criar uma experiência de usuário dinâmica.
-   **Backend e Lógica:** Toda a lógica de negócios, manipulação de dados e integrações são escritas em Python.
-   **Banco de Dados:** O sistema utiliza SQLite (`maintenance.db`) para armazenar todos os dados de forma persistente, garantindo leveza e facilidade de implantação.
-   **Estrutura Multi-página:** O projeto utiliza a estrutura de páginas do Streamlit, com a lógica de cada módulo separada em arquivos na pasta `pages/`.

---

## 🏁 Como Começar
Siga os passos abaixo para executar a aplicação em seu ambiente local.

### Pré-requisitos
-   Python 3.8 ou superior.
-   Gerenciador de pacotes `pip`.

### Instalação
1.  **Clone o repositório:**
    ```sh
    git clone [https://github.com/theofeitoza/Maintence.git](https://github.com/theofeitoza/Maintence.git)
    ```
2.  **Navegue até o diretório do projeto:**
    ```sh
    cd Maintence
    ```
3.  **Crie um ambiente virtual (recomendado):**
    ```sh
    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
4.  **Instale as dependências necessárias:** *(Nota: Crie um arquivo `requirements.txt` ou instale as bibliotecas principais manualmente)*
    ```sh
    pip install streamlit pandas sqlalchemy pillow
    ```

### Execução
1.  **Geração de Dados (Opcional):** Se for a primeira vez executando, você pode usar o script `gerador_de_dados.py` para popular o banco de dados com informações de exemplo.
    ```sh
    python gerador_de_dados.py
    ```
2.  **Inicie a aplicação Streamlit:**
    ```sh
    streamlit run App.py
    ```
3.  Abra seu navegador e acesse o endereço fornecido no terminal (geralmente `http://localhost:8501`).

---

## 📸 Screenshots

*(Adicione aqui os screenshots como login.jpg, kpis.jpg, etc.)*

**Tela inicial do sistema:**

**Dashboard de KPIs:**

---

<div align="left">
  <a href="#top">⬆ Voltar ao topo</a>
</div>
