def buscar_livro(titulo: str = "", autor: str = "") -> dict:
    """
    Busca os dados de um livro na biblioteca a partir do banco SQLite.

    Args:
        titulo (str): O título do livro a ser procurado.
        autor (str): O autor do livro a ser procurado.

    Returns:
        dict: Dados do livro ou mensagem de erro.
    """
    try:
        import sqlite3
        print("Buscando livro")
        conn = sqlite3.connect("./multi_agents/biblioteca.db")
        cursor = conn.cursor()

        if titulo and autor:
            cursor.execute("""
                SELECT titulo, autor, disponibilidade, exemplares_disponiveis
                FROM livros
                WHERE LOWER(titulo) = LOWER(?) AND LOWER(autor) = LOWER(?)
            """, (titulo, autor))
        elif titulo:
            cursor.execute("""
                SELECT titulo, autor, disponibilidade, exemplares_disponiveis
                FROM livros
                WHERE LOWER(titulo) = LOWER(?)
            """, (titulo,))
        elif autor:
            cursor.execute("""
                SELECT titulo, autor, disponibilidade, exemplares_disponiveis
                FROM livros
                WHERE LOWER(autor) = LOWER(?)
            """, (autor,))
        else:
            return {
                "error_message": "É necessário informar pelo menos o título ou o autor do livro."
            }

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
                "error_message": "Livro não encontrado no acervo."
            }

    except Exception as e:
        print(e)
        return {
            "error_message": f"Erro ao acessar o banco: {str(e)}"
        }