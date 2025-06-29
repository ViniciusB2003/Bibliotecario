import datetime
import sqlite3
from zoneinfo import ZoneInfo
from google.adk.agents import Agent


# Função para obter dados do banco no mesmo formato do dicionário
db_path = "./multi_agents/biblioteca.db"
def obter_acervo_do_banco(db_path: str = db_path) -> dict:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT titulo, autor, isbn, exemplares_total, exemplares_disponiveis,
                   (exemplares_disponiveis > 0) as disponibilidade
            FROM livros
        ''')
        acervo = {}
        for row in cursor.fetchall():
            titulo, autor, isbn, total, disponiveis, disponibilidade = row
            acervo[titulo] = {
                "autor": autor,
                "disponibilidade": bool(disponibilidade),
                "exemplares_total": total,
                "exemplares_disponiveis": disponiveis,
                "isbn": isbn
            }
        return acervo

# Acesso os livros do banco:
acervo_biblioteca = obter_acervo_do_banco()

# Registro de empréstimos
emprestimos_ativos = {}

def buscar_livro(nome_livro: str, nome_usuario: str) -> dict:
    livro = acervo_biblioteca.get(nome_livro)
    if livro:
        return {
            "status": "success",
            "nome_livro": nome_livro,
            "autor": livro["autor"],
            "isbn": livro["isbn"],
            "disponibilidade": livro["disponibilidade"],
            "exemplares_total": livro["exemplares_total"],
            "exemplares_disponiveis": livro["exemplares_disponiveis"]
        }
    else:
        return {
            "status": "error",
            "error_message": f"Livro '{nome_livro}' não encontrado no acervo da biblioteca."
        }

def realizar_emprestimo(nome_livro: str, nome_usuario: str, dias_emprestimo: int = 14) -> dict:
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Busca o id_usuario
            cursor.execute(
                "SELECT id FROM usuarios WHERE LOWER(nome) = LOWER(?) OR LOWER(nome) LIKE LOWER(?) || ' %' LIMIT 1",
                (nome_usuario, nome_usuario)
            )
            usuario_row = cursor.fetchone()
            if not usuario_row:
                return {"status": "error", "error_message": f"Usuário '{nome_usuario}' não encontrado."}
            id_usuario = usuario_row[0]

            # Busca o id_livro
            cursor.execute(
                "SELECT id FROM livros WHERE LOWER(titulo) = LOWER(?) LIMIT 1",
                (nome_livro,)
            )
            livro_row = cursor.fetchone()
            if not livro_row:
                return {"status": "error", "error_message": f"Livro '{nome_livro}' não encontrado."}
            id_livro = livro_row[0]

            # Verifica disponibilidade
            cursor.execute("SELECT exemplares_disponiveis FROM livros WHERE id = ?", (id_livro,))
            row = cursor.fetchone()
            if not row or row[0] <= 0:
                return {"status": "error", "error_message": "Livro não disponível para empréstimo."}

            # Atualiza exemplares disponíveis
            cursor.execute(
                "UPDATE livros SET exemplares_disponiveis = exemplares_disponiveis - 1, disponibilidade = CASE WHEN exemplares_disponiveis - 1 > 0 THEN 1 ELSE 0 END WHERE id = ?",
                (id_livro,)
            )

            # Cria o lançamento na tabela emprestimos
            data_emprestimo = datetime.datetime.now()
            data_devolucao = data_emprestimo + datetime.timedelta(days=dias_emprestimo)
            cursor.execute(
                """
                INSERT INTO emprestimos (id_usuario, id_livro, data_emprestimo, data_devolucao, devolvido)
                VALUES (?, ?, ?, ?, 0)
                """,
                (
                    id_usuario,
                    id_livro,
                    data_emprestimo.strftime("%Y-%m-%d %H:%M:%S"),
                    data_devolucao.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
        return {
            "status": "success",
            "message": "Empréstimo realizado com sucesso!",
            "detalhes": {
                "livro": nome_livro,
                "usuario": nome_usuario,
                "data_emprestimo": data_emprestimo.strftime("%d/%m/%Y"),
                "data_devolucao": data_devolucao.strftime("%d/%m/%Y"),
                "dias_emprestimo": dias_emprestimo
            }
        }
    except Exception as e:
        return {"status": "error", "error_message": f"Erro ao registrar empréstimo: {str(e)}"}

def devolver_livro(nome_livro: str, nome_usuario: str) -> dict:
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Busca o id_usuario
            cursor.execute(
                "SELECT id FROM usuarios WHERE LOWER(nome) = LOWER(?) OR LOWER(nome) LIKE LOWER(?) || ' %' LIMIT 1",
                (nome_usuario, nome_usuario)
            )
            usuario_row = cursor.fetchone()
            if not usuario_row:
                return {"status": "error", "error_message": f"Usuário '{nome_usuario}' não encontrado."}
            id_usuario = usuario_row[0]

            # Busca o id_livro
            cursor.execute(
                "SELECT id FROM livros WHERE LOWER(titulo) = LOWER(?) LIMIT 1",
                (nome_livro,)
            )
            livro_row = cursor.fetchone()
            if not livro_row:
                return {"status": "error", "error_message": f"Livro '{nome_livro}' não encontrado."}
            id_livro = livro_row[0]

            # Busca o empréstimo ativo
            cursor.execute(
                "SELECT data_emprestimo, data_devolucao FROM emprestimos WHERE id_usuario = ? AND id_livro = ? AND devolvido = 0 ORDER BY data_emprestimo DESC LIMIT 1",
                (id_usuario, id_livro)
            )
            row = cursor.fetchone()
            if not row:
                return {"status": "error", "error_message": "Nenhum empréstimo ativo encontrado para este usuário e livro."}
            data_emprestimo, data_devolucao_prevista = row
            data_devolucao_real = datetime.datetime.now()
            atraso = (data_devolucao_real - datetime.datetime.strptime(data_devolucao_prevista, "%Y-%m-%d %H:%M:%S")).days

            # Atualiza o livro
            cursor.execute(
                "UPDATE livros SET exemplares_disponiveis = exemplares_disponiveis + 1, disponibilidade = 1 WHERE id = ?",
                (id_livro,)
            )
            # Marca o empréstimo como devolvido
            cursor.execute(
                """
                UPDATE emprestimos
                SET devolvido = 1
                WHERE id_usuario = ? AND id_livro = ? AND devolvido = 0
                """,
                (id_usuario, id_livro)
            )
            conn.commit()
        resultado = {
            "status": "success",
            "message": "Devolução realizada com sucesso!",
            "detalhes": {
                "livro": nome_livro,
                "usuario": nome_usuario,
                "data_emprestimo": data_emprestimo,
                "data_devolucao_prevista": data_devolucao_prevista,
                "data_devolucao_real": data_devolucao_real.strftime("%d/%m/%Y"),
                "atraso_dias": max(0, atraso)
            }
        }
        if atraso > 0:
            resultado["aviso"] = f"Livro devolvido com {atraso} dia(s) de atraso."
        return resultado
    except Exception as e:
        return {"status": "error", "error_message": f"Erro ao processar devolução: {str(e)}"}


def consultar_emprestimos_usuario(nome_usuario: str) -> dict:
    emprestimos_usuario = []
    for chave, emprestimo in emprestimos_ativos.items():
        if emprestimo["nome_usuario"] == nome_usuario:
            data_atual = datetime.datetime.now()
            dias_restantes = (emprestimo["data_devolucao"] - data_atual).days
            emprestimos_usuario.append({
                "livro": emprestimo["nome_livro"],
                "data_emprestimo": emprestimo["data_emprestimo"].strftime("%d/%m/%Y"),
                "data_devolucao": emprestimo["data_devolucao"].strftime("%d/%m/%Y"),
                "dias_restantes": dias_restantes,
                "status": "Em atraso" if dias_restantes < 0 else "No prazo"
            })
    if emprestimos_usuario:
        return {
            "status": "success",
            "usuario": nome_usuario,
            "total_emprestimos": len(emprestimos_usuario),
            "emprestimos": emprestimos_usuario
        }
    else:
        return {
            "status": "success",
            "message": f"Usuário '{nome_usuario}' não possui empréstimos ativos."
        }

def listar_acervo_disponivel() -> dict:
    livros_disponiveis = []
    for nome_livro, dados in acervo_biblioteca.items():
        if dados["disponibilidade"] and dados["exemplares_disponiveis"] > 0:
            livros_disponiveis.append({
                "titulo": nome_livro,
                "autor": dados["autor"],
                "isbn": dados["isbn"],
                "exemplares_disponiveis": dados["exemplares_disponiveis"],
                "exemplares_total": dados["exemplares_total"]
            })
    return {
        "status": "success",
        "total_livros_disponiveis": len(livros_disponiveis),
        "livros_disponiveis": livros_disponiveis
    }

# Criação do agente especializado em empréstimos
agente_emprestimo = Agent(
    name="bibliotecario_emprestimos",
    model="gemini-2.0-flash",
    description=(
        "Agente especializado em gerenciar empréstimos e devoluções de livros da biblioteca"
    ),
    instruction=(
        "Você é um bibliotecário atencioso e cordial, especializado no atendimento ao público e na gestão de empréstimos de livros.\n"
        "Voce é um subagente do root_agent, que é o agente principal da biblioteca. voce irá auxiliar na consulta e realização de empréstimos\n"
        "Seu papel é ajudar os usuários como se estivesse em uma biblioteca real. Suas principais funções são:\n"
        "Sempre comece a conversa fazendo uma saudação ao usuário, como Bom dia!, Boa tarde, Boa Noite! \n"
        "Em seguida diga: Como posso ajudar nas suas leituras hoje? \n"
        "1. Consultar a disponibilidade de livros no acervo.\n"
        "2. Realizar empréstimos de livros para os usuários, explicando prazos e procedimentos.\n"
        "3. Processar devoluções de livros e atualizar o sistema.\n"
        "4. Consultar os empréstimos ativos de um usuário e informar os prazos de devolução.\n"
        "5. Listar os livros disponíveis para empréstimo.\n"
        "Durante o atendimento, sempre seja prestativo e claro.\n" 
        "Para realizar um empréstimo, colete as seguintes informações:\n"
        "- Título exato do livro desejado \n"
        "- Período desejado para o empréstimo (o padrão é 14 dias, mas pode ser ajustado se necessário) \n"
        "Forneça informações objetivas sobre disponibilidade, prazos e instruções de devolução. \n"
        "Atue de forma humana, como um funcionário real de biblioteca, prezando por um atendimento educado e eficiente."
    ),
    tools=[
        buscar_livro,
        realizar_emprestimo,
        devolver_livro,
        consultar_emprestimos_usuario,
        listar_acervo_disponivel
    ],
)

if __name__ == "__main__":
    print("=== Sistema de Empréstimos da Biblioteca ===")
    print("Agente Bibliotecário de Empréstimos inicializado!")
    print("Funcionalidades disponíveis:")
    print("- Buscar livros")
    print("- Realizar empréstimos")
    print("- Processar devoluções")
    print("- Consultar empréstimos do usuário")
    print("- Listar acervo disponível")