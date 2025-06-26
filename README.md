# 📚 Bibliotecário ADK

Um agente inteligente construído com o [Google ADK](https://github.com/google/adk) que permite consultar livros em uma biblioteca utilizando um banco de dados SQLite.

## 🚀 Funcionalidades

- Consulta de livros com título e autor.
- Verificação de disponibilidade em tempo real via banco SQLite.
- Agente conversacional com interface web do ADK.
- Integração com múltiplas ferramentas (`tools`) do ADK.
- **Futuramente:** ferramentas adicionais como:
  - 📖 Empréstimo de livros
  - 🤖 Recomendação de leitura personalizada

## 🧠 Tecnologias

- Python 3.10+
- Google ADK (Agent Development Kit)
- SQLite (banco local embutido no Python)
- Gemini API (via chave da Google)

## 📂 Estrutura do Projeto

multi_tool_agent/

├── multi_agents/

│ ├── agent.py # Agente principal (root_agent)

│ ├── busca.py # Tool: busca de livros no SQLite

│ ├── emprestimo.py # Tool: empréstimo de livros

│ ├── recomendacao.py # Tool: recomendação de livros

│ ├── biblioteca.db # Banco de dados com os livros

│ ├── init.py

│ └── .env # Configurações (API Key)

├── requirements.txt

└── README.md


## 🚀 Como rodar o projeto

1. Clone o repositório

      git clone https://github.com/ViniciusB2003/Bibliotecario.git
  
      cd Bibliotecario/multi_tool_agent


2. Crie e ative um ambiente virtual

Windows:

    python -m venv .venv
    
    .venv\Scripts\activate


Linux/macOS:

    python -m venv .venv
    
    source .venv/bin/activate

3. Instale as dependências

       pip install -r requirements.txt


4. Configure sua chave da API Gemini
   
Crie um arquivo .env dentro da pasta multi_agents com o seguinte conteúdo:

    GOOGLE_API_KEY=your_api_key_aqui
    GOOGLE_GENAI_USE_VERTEXAI=FALSE

5. Rode o agente
   
Entre na pasta multi_agents e execute:

    adk web

Acesse no navegador: http://127.0.0.1:8000





## 🗃 Exemplo de uso

Você pode iniciar a conversa dizendo:

Olá, quero saber se o livro "1984" está disponível!

O agente responderá com o autor e a disponibilidade do livro, consultando diretamente o banco de dados biblioteca.db.






## 📌 Observações

O banco de dados biblioteca.db precisa estar na pasta multi_agents.
