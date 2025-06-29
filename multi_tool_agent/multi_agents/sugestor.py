import sqlite3
from google.adk.agents import Agent

def sugerir_livros_por_autor(autor: str) -> dict:
    """
    Sugere livros do mesmo autor disponíveis no acervo da biblioteca.
    
    Args:
        autor (str): Nome do autor para buscar livros relacionados.
        
    Returns:
        dict: {
            "status": "success"|"error",
            "livros": [{"titulo": str, "disponibilidade": bool, "exemplares_disponiveis": int}] | None,
            "error_message": str | None
        }
    """
    try:
        conn = sqlite3.connect("./multi_agents/biblioteca.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT titulo, disponibilidade, exemplares_disponiveis
            FROM livros
            WHERE LOWER(autor) = LOWER(?)
            ORDER BY titulo
        """, (autor,))
        
        livros = []
        for row in cursor.fetchall():
            titulo, disponibilidade, exemplares = row
            livros.append({
                "titulo": titulo,
                "disponibilidade": bool(disponibilidade),
                "exemplares_disponiveis": exemplares
            })
        
        conn.close()
        
        if livros:
            return {
                "status": "success",
                "livros": livros,
                "message": f"Encontrados {len(livros)} livros do autor {autor}"
            }
        else:
            return {
                "status": "success",
                "livros": [],
                "message": f"Nenhum outro livro do autor {autor} encontrado no acervo."
            }
            
    except Exception as e:
        return {
            "status": "error",
            "livros": None,
            "error_message": f"Erro ao buscar sugestões: {str(e)}"
        }
        


def sugerir_livros_por_genero(genero: str) -> dict:
    """
    Sugere livros do mesmo gênero disponíveis no acervo da biblioteca.

    Args:
        genero (str): Nome do gênero para buscar livros relacionados.

    Returns:
        dict: {
            "status": "success"|"error",
            "livros": [{"titulo": str, "disponibilidade": bool, "exemplares_disponiveis": int}] | None,
            "error_message": str | None
        }
    """
    try:
        conn = sqlite3.connect("./multi_agents/biblioteca.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT titulo, disponibilidade, exemplares_disponiveis
            FROM livros
            WHERE LOWER(genero) = LOWER(?)
            ORDER BY titulo
        """, (genero,))
        
        livros = []
        for row in cursor.fetchall():
            titulo, disponibilidade, exemplares = row
            livros.append({
                "titulo": titulo,
                "disponibilidade": bool(disponibilidade),
                "exemplares_disponiveis": exemplares
            })
        
        conn.close()
        
        if livros:
            return {
                "status": "success",
                "livros": livros,
                "message": f"Encontrados {len(livros)} livros do gênero {genero}"
            }
        else:
            return {
                "status": "success",
                "livros": [],
                "message": f"Nenhum outro livro do gênero {genero} encontrado no acervo."
            }
            
    except Exception as e:
        return {
            "status": "error",
            "livros": None,
            "error_message": f"Erro ao buscar sugestões: {str(e)}"
        }

agente_sugestor = Agent(
    name="sugestor_leituras",
    model="gemini-2.0-flash",
    description="Agente especializado em sugerir livros do mesmo autor ou gênero",
    instruction=(
        "Você é um assistente de biblioteca especializado em recomendações de leitura.\n"
        "Sua função é sugerir outros livros do mesmo autor quando um usuário demonstrar interesse em uma obra.\n\n"
        
        "Instruções de funcionamento:\n"
        "1. Sempre que um usuário mencionar um livro ou autor ou gênero, ofereça para verificar se há outras obras do mesmo autor ou do gênero que o usuario informou.\n"
        "2. Utiliza a função sugerir_livros_por_genero caso o usuário mencione um gênero e a função sugerir_livros_por_autor caso mencione um autor.\n"
        "3. Se não encontrar outros livros do autor, informe educadamente e sugira consultar o acervo completo.\n"
        "4. Mantenha um tom amigável e encorajador para promover a leitura.\n\n"
        
        "Exemplo de interação:\n"
        "Usuário: 'Estou interessado em livros de Machado de Assis'\n"
        "Você: 'Encontrei 3 obras de Machado de Assis em nosso acervo: Dom Casmurro (disponível), Memórias Póstumas de Brás Cubas (disponível), e Quincas Borba (indisponível no momento).'"
    ),
    tools=[sugerir_livros_por_autor,sugerir_livros_por_genero],
)