
def buscar_livro(titulo: str) -> dict:
    """
    Busca os dados de um livro na biblioteca a partir do banco SQLite.

    Args:
        titulo (str): O título do livro a ser procurado.

    Returns:
        dict: {
             titulo (str): Título do livro,
             autor (str): Autor do livro,
             disponibilidade (bool): Indica se o livro está disponível,
             exemplares_disponiveis (int): Número de exemplares disponíveis
        } || dict: {
             error_message (str): Mensagem de erro caso o livro não seja encontrado ou ocorra um erro na busca.
             }
    """
    try:
        import sqlite3
        print("Buscando livro")
        conn = sqlite3.connect("./multi_agents/biblioteca.db")
        cursor = conn.cursor()

        # Consulta o livro ignorando letras maiúsculas/minúsculas
        cursor.execute("""
            SELECT titulo, autor, disponibilidade, exemplares_disponiveis
            FROM livros
            WHERE LOWER(titulo) = LOWER(?)
        """, (titulo,))

        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            titulo, autor, disponibilidade, exemplares_disponiveis = resultado
            return {
                "titulo": titulo,
                "autor": autor,
                "disponibilidade": bool(disponibilidade),
                "exemplares_disponiveis": exemplares_disponiveis
            }
        else:
            return {
                "error_message": f"Livro '{titulo}' não encontrado no acervo."
            }

    except Exception as e:
        print(e)
        return {
            "error_message": f"Erro ao acessar o banco: {str(e)}"
        }
