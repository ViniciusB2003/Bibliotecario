import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.agents import LlmAgent, BaseAgent

##from multi_tool_agent.multi_agents.emprestimo import obter_acervo_do_banco
from .busca import buscar_livro
from .emprestimo import (realizar_emprestimo,devolver_livro,consultar_emprestimos_usuario, listar_acervo_disponivel)
from .emprestimo import agente_emprestimo
from .sugestor import agente_sugestor
#CRIAR AMBIENTE VIRTUAL .VENV

def usuario_existe(nome_usuario: str) -> dict:
    """
    Verifica se o usuário existe na tabela usuarios do banco de dados,
    aceitando tanto o nome completo quanto apenas o primeiro nome.

    Args:
        nome_usuario (str): Nome informado pelo usuário.

    Returns:
        dict: {"existe": True/False, "nome_completo": str ou None, "mensagem": ...}
    """
    try:
        import sqlite3
        conn = sqlite3.connect("./multi_agents/biblioteca.db")
        cursor = conn.cursor()
        # Busca por nome completo ou nomes que começam com o primeiro nome informado
        cursor.execute(
            """
            SELECT nome FROM usuarios
            WHERE LOWER(nome) = LOWER(?)
               OR LOWER(nome) LIKE LOWER(?) || ' %'
            LIMIT 1
            """,
            (nome_usuario, nome_usuario)
        )
        resultado = cursor.fetchone()
        conn.close()
        if resultado:
            return {
                "existe": True,
                "nome_completo": resultado[0],
                "mensagem": f"Usuário reconhecido: {resultado[0]}"
            }
        else:
            return {
                "existe": False,
                "nome_completo": None,
                "mensagem": f"Usuário '{nome_usuario}' não cadastrado. Entre em contato com o administrador."
            }
    except Exception as e:
        return {
            "existe": False,
            "nome_completo": None,
            "mensagem": f"Erro ao acessar o banco de dados: {str(e)}"
        }


root_agent = Agent(
    name="Bibliotecário",
    model="gemini-2.0-flash",
    description=(
        "Agente responsável por consultar livros de uma biblioteca"
    ),
    instruction=(
        "Você é um agente especializado em fornecer informações de todo o acervo de livros da biblioteca"+
        "Primeiramente voce irá questionar o nome do usuário e questionar o livro que ele busca"+
        "Voce irá verificar se o nome do usuário já existe no banco de dados na tabela usuarios, se não existir, você pedirá para o usuario entrar em contato com o administrador"+
        "Sempre que realizar um empréstimo, informar ao usuario a data de devolução do livro, o máximo de dias de emprestimo tambem (por padrão 14 dias mas pode ser mais se necessário)"+
        "O Usuário poderá te informar o titulo do livro e ou o autor, e voce poderá buscar por um ou outro, ou ambos"+
        "Você irá buscar o livro no banco de dados SQLite, e retornar as informações do livro"+
        "Em seguida você irá buscar o livro no acervo e retornar a informação se o livro está disponível ou não"+
        "Em caso de erro, você irá retornar uma mensagem de erro informando o que aconteceu de forma detalhada e concisa, como uma estrutura de try catch faria, qual foi o motivo do erro e etc."
    ),
    sub_agents=[agente_emprestimo,agente_sugestor],
    tools=[buscar_livro,usuario_existe],
)

##realizar_emprestimo,devolver_livro,consultar_emprestimos_usuario,listar_acervo_disponivel,