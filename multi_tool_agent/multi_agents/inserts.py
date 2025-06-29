import sqlite3
 
# Conectar ao banco existente
conn = sqlite3.connect("multi_tool_agent/multi_agents/biblioteca.db")
cursor = conn.cursor()
 
# Atualizar todos os livros existentes com os novos valores
cursor.execute("""
    UPDATE livros SET exemplares_disponiveis = 5 where id = 3
""")
 
conn.commit()
conn.close()

print("Livro atualizado com sucesso!")