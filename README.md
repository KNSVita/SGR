# Sistema de Gerenciamento de Ranking (SGR)

Este é um sistema web desenvolvido com Flask que permite o gerenciamento de classificações de alunos e a geração de rankings baseados em notas calculadas a partir de planilhas.

## Funcionalidades

*   **Upload de Planilhas**: Faça upload de arquivos CSV ou Excel contendo dados de alunos e suas notas (Trabalho, AV, AVS).
*   **Definição de Parâmetros de Classificação**: Para cada disciplina (classificação), defina pesos para as notas de Trabalho (`peso_real_trab`), Avaliação (`peso_real_av`) e a base da nota AV/AVS (`peso_orig_av`).
*   **Cálculo de Notas Finais**: O sistema calcula automaticamente a nota final de cada aluno com base nas notas da planilha e nos pesos definidos, considerando cenários como sobra de nota de trabalho e a melhor nota entre AV e AVS.
*   **Geração de Ranking**: Visualize um ranking ordenado dos alunos para cada classificação, baseado na nota final calculada. O ranking é gerado utilizando o algoritmo Merge Sort.
*   **Persistência de Dados**: As classificações e os dados dos alunos são armazenados em um banco de dados (SQLite por padrão, configurável para PostgreSQL).
*   **Interface Web Intuitiva**: Uma interface de usuário simples para upload de arquivos, visualização de classificações e acesso aos rankings.

## Tecnologias Utilizadas

*   **Backend**: Python com Flask
*   **Banco de Dados**: SQLAlchemy (compatível com SQLite e PostgreSQL)
*   **Processamento de Dados**: Pandas
*   **Ordenação**: Implementação customizada do algoritmo Merge Sort
*   **Frontend**: HTML, CSS, JavaScript (Jinja2 para templates)

## Como Rodar o Projeto (Localmente)

### Pré-requisitos

*   Python 3.x
*   pip (gerenciador de pacotes do Python)

### Instalação

1.  **Clone o repositório**:
    ```bash
    git clone https://github.com/seu-usuario/SGR.git
    cd SGR
    ```

2.  **Crie e ative um ambiente virtual**:
    ```bash
    python -m venv .venv
    # No Windows
    .venv\Scripts\activate
    # No macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

### Configuração do Banco de Dados

Por padrão, o sistema utiliza SQLite e cria um arquivo `local_test.db` na pasta `instance/`.

Para usar PostgreSQL, defina a variável de ambiente `DATABASE_URL` antes de iniciar a aplicação:
```bash
# Exemplo para PostgreSQL
# No Windows
$env:DATABASE_URL="postgresql://user:password@host:port/database_name"
# No macOS/Linux
export DATABASE_URL="postgresql://user:password@host:port/database_name"
```

### Executando a Aplicação

1.  **Inicialize o banco de dados (cria as tabelas)**:
    ```bash
    python -c "from app import app, db; with app.app_context(): db.create_all()"
    ```

2.  **Inicie o servidor Flask**:
    ```bash
    python app.py
    ```

A aplicação estará disponível em `http://127.0.0.1:5000/`.

## Estrutura do Projeto

```
.
├── algoritmos.py           # Implementação do Merge Sort
├── app.py                  # Aplicação Flask principal, rotas e lógica de negócio
├── requirements.txt        # Dependências do projeto
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
│   ├── style.css
│   ├── script.js
│   └── assets/
│       └── logo_wyden.png
└── templates/              # Templates HTML (Jinja2)
    ├── base.html
    ├── index.html          # Página principal com formulário de upload e lista de classificações
    └── ranking.html        # Página para exibir o ranking de uma classificação
```

## Como Usar

1.  Acesse a página inicial (`/`).
2.  Preencha o nome da disciplina e os pesos desejados.
3.  Faça upload de uma planilha (CSV ou Excel) com as colunas `nome`, `Trab`, `AV` e `AVS`.
4.  Clique em "Processar Planilha".
5.  Após o processamento, a classificação aparecerá na lista. Clique em "Ver Ranking" para visualizar a lista de alunos ordenada.
6.  É possível excluir classificações existentes.

## Contribuição

Sinta-se à vontade para contribuir com o projeto. Por favor, siga as boas práticas de desenvolvimento e envie Pull Requests.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.