import sqlite3
 
# Conectar ao banco existente
conn = sqlite3.connect("multi_tool_agent/multi_agents/biblioteca.db")
cursor = conn.cursor()
 
# Atualizar todos os livros existentes com os novos valores
cursor.execute("""
    delete from emprestimos
""")
 
conn.commit()
conn.close()

print("Empréstimos deletados com sucesso!")