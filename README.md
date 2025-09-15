<div align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&size=30&pause=1000&color=FF0000&center=true&vCenter=true&width=900&lines=Sistema+de+Gerenciamento+de+Biblioteca;Meu+primeiro+projeto+de+curso!;Desenvolvido+em+Python+%F0%9F%90%8D" alt="Animação de Digitação">
  </a>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/Status-Finalizado-green?style=for-the-badge" alt="Status Badge"/>
  <img src="https://img.shields.io/badge/Licen%C3%A7a-MIT-blue?style=for-the-badge" alt="License Badge"/>
</div>

---

### 📖 Sobre o Projeto

Bem-vindo ao meu Gerenciador de Biblioteca Pessoal! Este projeto representa um marco importante na minha jornada como desenvolvedor: foi o **primeiro grande projeto que desenvolvi durante meu curso de Desenvolvimento de Sistemas**. É uma aplicação de console (CLI) robusta, criada em Python, para catalogar e gerenciar uma coleção pessoal de filmes e séries.

O objetivo era criar um sistema completo, desde a autenticação de usuário até a integração com uma API externa, aplicando conceitos fundamentais de programação e estruturação de dados.

---

### ✨ Funcionalidades Principais

Este sistema foi construído com um conjunto rico de funcionalidades para oferecer uma experiência de gerenciamento completa:

* **🔐 Sistema de Login Seguro:** Proteção por senha com limite de tentativas para acesso ao sistema.
* **🌐 Integração com API OMDb:** Busca automática de informações detalhadas de filmes e séries, incluindo sinopse, elenco, notas e pôsteres.
* **➕ Adição Manual e Automática:** Cadastre itens manualmente ou simplesmente busque online e adicione à sua biblioteca com um comando.
* **📑 Gerenciamento CRUD Completo:** Crie, Liste, Edite e Exclua qualquer item da sua coleção.
* **⭐ Sistema de Avaliação e Favoritos:** Dê notas de 0 a 10 e marque seus títulos preferidos.
* **📊 Estatísticas da Biblioteca:** Obtenha um resumo da sua coleção, como total de itens, média de notas e gêneros mais comuns.
* **🔍 Pesquisa e Filtragem Avançada:** Busque itens pelo título ou filtre toda a sua coleção por gênero.
* **🔀 Sugestões Inteligentes:** Receba sugestões aleatórias da sua lista "Para assistir" ou descubra novos filmes online por gênero.
* **💾 Importação e Exportação:** Exporte toda a sua biblioteca para um arquivo `.csv` ou importe dados a partir de um.
* **🛠️ Utilitários do Sistema:** Ferramentas para criar e restaurar backups, visualizar histórico de ações e verificar itens duplicados.
* **🎨 Interface Colorida:** Uso da biblioteca `colorama` para uma experiência de usuário mais agradável e intuitiva no terminal.

---

### 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias e bibliotecas:

<p align="center">
  <a href="#"><img src="https://skillicons.dev/icons?i=python,git,bash,vscode,linux" /></a>
</p>

* **Linguagem Principal:** Python 3
* **Bibliotecas:** `requests` (para requisições à API), `colorama` (para estilização do terminal), `json`, `csv`, `os`, `shutil`.
* **API Externa:** [OMDb API](http://www.omdbapi.com/) (The Open Movie Database).
* **Formato de Dados:** `JSON` para o banco de dados principal e `CSV` para importação/exportação.

---

### 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para ter o projeto rodando na sua máquina.

#### Pré-requisitos
* **Python 3.x** instalado.
* Uma chave de API da **OMDb**. É grátis e você pode conseguir uma [aqui](http://www.omdbapi.com/apikey.aspx).

#### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/wallax0x/biblioteca
    cd biblioteca
    ```

2.  **Crie um arquivo de dependências (se ainda não existir):**
    Este projeto usa bibliotecas externas. Crie um arquivo `requirements.txt` para gerenciá-las.
    ```bash
    # Crie um arquivo chamado requirements.txt e adicione as seguintes linhas:
    requests
    colorama
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure sua Chave de API:**
    Abra o arquivo `biblioteca.py` em um editor ex: nano de texto e substitua o valor da variável `API_KEY` pela sua chave pessoal da OMDb.
    ```python
    # Linha 12 (aproximadamente)
    API_KEY = 'SUA_CHAVE_AQUI' 
    ```

5.  **Execute o programa:**
    ```bash
    python biblioteca.py
    ```
    Na primeira vez, o sistema pedirá para você criar uma senha. Depois disso, você poderá acessar todas as funcionalidades!

---
### 📂 Estrutura do Projeto
```bash
├── backups_biblioteca/     # Pasta para backups automáticos
├── main.py                 # Arquivo principal com todo o código
├── biblioteca.json         # O "banco de dados" onde os filmes/séries são salvos
├── historico.log           # Registra todas as ações importantes
├── senha.txt               # Armazena a senha de acesso
└── requirements.txt        # Lista de dependências Python
```
