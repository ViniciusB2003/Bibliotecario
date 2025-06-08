import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

# Acervo da biblioteca. Subistituir pelo banco depois.
acervo_biblioteca = {
    "O Senhor dos Anéis": {
        "autor": "J.R.R. Tolkien", 
        "disponibilidade": True,
        "exemplares_total": 3,
        "exemplares_disponiveis": 2,
        "isbn": "978-0544003415"
    },
    "1984": {
        "autor": "George Orwell", 
        "disponibilidade": False,
        "exemplares_total": 2,
        "exemplares_disponiveis": 0,
        "isbn": "978-0452284234"
    },
    "Dom Casmurro": {
        "autor": "Machado de Assis", 
        "disponibilidade": True,
        "exemplares_total": 4,
        "exemplares_disponiveis": 3,
        "isbn": "978-8525406958"
    },
    "Harry Potter e a Pedra Filosofal": {
        "autor": "J.K. Rowling",
        "disponibilidade": True,
        "exemplares_total": 5,
        "exemplares_disponiveis": 4,
        "isbn": "978-8532511010"
    },
    "O Pequeno Príncipe": {
        "autor": "Antoine de Saint-Exupéry",
        "disponibilidade": True,
        "exemplares_total": 6,
        "exemplares_disponiveis": 5,
        "isbn": "978-8595081413"
    }
}

# Registro de empréstimos
emprestimos_ativos = {}

def buscar_livro(nome_livro: str, nome_usuario: str) -> dict:
    """
    Busca os dados de um livro na biblioteca utilizando o nome do livro fornecido pelo usuário.
    
    Args:
        nome_livro (str): O nome do livro a ser buscado.
        nome_usuario (str): O nome do usuário que está fazendo a busca.
    
    Returns:
        dict: Informações completas do livro incluindo disponibilidade.   
    """
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
    """
    Realiza o empréstimo de um livro para um usuário específico.
    
    Args:
        nome_livro (str): O nome do livro a ser emprestado.
        nome_usuario (str): O nome do usuário que está solicitando o empréstimo.
        dias_emprestimo (int): Número de dias para o empréstimo (padrão: 14 dias).
    
    Returns:
        dict: Status do empréstimo com detalhes da operação.
    """
    livro = acervo_biblioteca.get(nome_livro)
    
    if not livro:
        return {
            "status": "error",
            "error_message": f"Livro '{nome_livro}' não encontrado no acervo."
        }
    
    if not livro["disponibilidade"] or livro["exemplares_disponiveis"] <= 0:
        return {
            "status": "error",
            "error_message": f"Livro '{nome_livro}' não está disponível para empréstimo no momento."
        }
    
    # Verificar se o usuário já tem este livro emprestado
    chave_emprestimo = f"{nome_usuario}_{nome_livro}"
    if chave_emprestimo in emprestimos_ativos:
        return {
            "status": "error",
            "error_message": f"Usuário '{nome_usuario}' já possui o livro '{nome_livro}' emprestado."
        }
    
    # Realizar o empréstimo
    data_emprestimo = datetime.datetime.now()
    data_devolucao = data_emprestimo + datetime.timedelta(days=dias_emprestimo)
    
    # Atualizar disponibilidade no acervo
    acervo_biblioteca[nome_livro]["exemplares_disponiveis"] -= 1
    if acervo_biblioteca[nome_livro]["exemplares_disponiveis"] == 0:
        acervo_biblioteca[nome_livro]["disponibilidade"] = False
    
    # Registrar empréstimo
    emprestimos_ativos[chave_emprestimo] = {
        "nome_livro": nome_livro,
        "nome_usuario": nome_usuario,
        "data_emprestimo": data_emprestimo,
        "data_devolucao": data_devolucao,
        "dias_emprestimo": dias_emprestimo
    }
    
    return {
        "status": "success",
        "message": f"Empréstimo realizado com sucesso!",
        "detalhes": {
            "livro": nome_livro,
            "usuario": nome_usuario,
            "data_emprestimo": data_emprestimo.strftime("%d/%m/%Y"),
            "data_devolucao": data_devolucao.strftime("%d/%m/%Y"),
            "dias_emprestimo": dias_emprestimo
        }
    }

def devolver_livro(nome_livro: str, nome_usuario: str) -> dict:
    """
    Processa a devolução de um livro emprestado.
    
    Args:
        nome_livro (str): O nome do livro a ser devolvido.
        nome_usuario (str): O nome do usuário que está devolvendo o livro.
    
    Returns:
        dict: Status da devolução com detalhes da operação.
    """
    chave_emprestimo = f"{nome_usuario}_{nome_livro}"
    
    if chave_emprestimo not in emprestimos_ativos:
        return {
            "status": "error",
            "error_message": f"Não foi encontrado empréstimo ativo do livro '{nome_livro}' para o usuário '{nome_usuario}'."
        }
    
    emprestimo = emprestimos_ativos[chave_emprestimo]
    data_devolucao_real = datetime.datetime.now()
    data_devolucao_prevista = emprestimo["data_devolucao"]
    
    # Calcular atraso
    atraso = (data_devolucao_real - data_devolucao_prevista).days
    
    # Atualizar disponibilidade no acervo
    acervo_biblioteca[nome_livro]["exemplares_disponiveis"] += 1
    acervo_biblioteca[nome_livro]["disponibilidade"] = True
    
    # Remover empréstimo ativo
    del emprestimos_ativos[chave_emprestimo]
    
    resultado = {
        "status": "success",
        "message": f"Devolução realizada com sucesso!",
        "detalhes": {
            "livro": nome_livro,
            "usuario": nome_usuario,
            "data_emprestimo": emprestimo["data_emprestimo"].strftime("%d/%m/%Y"),
            "data_devolucao_prevista": data_devolucao_prevista.strftime("%d/%m/%Y"),
            "data_devolucao_real": data_devolucao_real.strftime("%d/%m/%Y"),
            "atraso_dias": max(0, atraso)
        }
    }
    
    if atraso > 0:
        resultado["aviso"] = f"Livro devolvido com {atraso} dia(s) de atraso."
    
    return resultado

def consultar_emprestimos_usuario(nome_usuario: str) -> dict:
    """
    Consulta todos os empréstimos ativos de um usuário específico.
    
    Args:
        nome_usuario (str): O nome do usuário para consultar empréstimos.
    
    Returns:
        dict: Lista de empréstimos ativos do usuário.
    """
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
    """
    Lista todos os livros disponíveis para empréstimo na biblioteca.
    
    Returns:
        dict: Lista de livros disponíveis com suas informações.
    """
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
    name="Bibliotecário de Empréstimos",
    model="gemini-2.0-flash",
    description=(
        "Agente especializado em gerenciar empréstimos e devoluções de livros da biblioteca"
    ),
    instruction=(
        "Você é um bibliotecário atencioso e cordial, especializado no atendimento ao público e na gestão de empréstimos de livros.\n"
        "Seu papel é ajudar os usuários como se estivesse em uma biblioteca real. Suas principais funções são:\n"
        "Sempre comece a conversa fazendo uma saudação ao usuário, como Bom dia!, Boa tarde, Boa Noite! \n"
        "Em seguida diga: Como posso ajudar nas suas leituras hoje? \n"

        "1. Consultar a disponibilidade de livros no acervo.\n"
        "2. Realizar empréstimos de livros para os usuários, explicando prazos e procedimentos.\n"
        " 3. Processar devoluções de livros e atualizar o sistema.\n"
        "4. Consultar os empréstimos ativos de um usuário e informar os prazos de devolução.\n"
        "5. Listar os livros disponíveis para empréstimo.\n"

        "Durante o atendimento, sempre seja prestativo e claro.\n" 
        "Para realizar um empréstimo, colete as seguintes informações:\n"

        "- Nome completo do usuário\n"
        "- Título exato do livro desejado \n"
        "- Período desejado para o empréstimo (o padrão é 14 dias, mas pode ser ajustado se necessário) \n"

        "Forneça informações objetivas sobre disponibilidade, prazos e instruções de devolução. \n"
        " Atue de forma humana, como um funcionário real de biblioteca, prezando por um atendimento educado e eficiente."
    ),
    tools=[
        buscar_livro,
        realizar_emprestimo,
        devolver_livro,
        consultar_emprestimos_usuario,
        listar_acervo_disponivel
    ],
)

# Exemplo de uso
if __name__ == "__main__":
    print("=== Sistema de Empréstimos da Biblioteca ===")
    print("Agente Bibliotecário de Empréstimos inicializado!")
    print("Funcionalidades disponíveis:")
    print("- Buscar livros")
    print("- Realizar empréstimos")
    print("- Processar devoluções")
    print("- Consultar empréstimos do usuário")
    print("- Listar acervo disponível")