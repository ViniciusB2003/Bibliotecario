import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
#CRIAR AMBIENTE VIRTUAL .VENV
def get_weather(city: str) -> dict: #Descrever para a IA o que ela deve fazer
    """Retrieves the current weather report for a specified city.

    Args: #Parametros com descrição e seu signficado
        city (str): The name of the city for which to retrieve the weather report.

    Returns: # O Que retornar de dados para o solicitante
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}

def buscar_livro(nome_livro: str, nome_usuario: str) -> dict:
    """
    Busca os dados de um livro na biblioteca. utilizando o nome do livro fornecido pelo usuário.
    Args:
        nome_livro (str): O nome do livro a ser buscado.
        nome_usuario (str): O nome do usuário que está fazendo a busca.
    Returns:
        dict: Nome do livro, autor do livro, disponibilidade do livro na biblioteca.   
    """
    # Simulação de busca em um acervo de livros
    acervo = {
        "O Senhor dos Anéis": {"autor": "J.R.R. Tolkien", "disponibilidade": True},
        "1984": {"autor": "George Orwell", "disponibilidade": False},
        "Dom Casmurro": {"autor": "Machado de Assis", "disponibilidade": True},
    }

    livro = acervo.get(nome_livro)
    
    if livro:
        return {
            "nome_livro": nome_livro,
            "autor": livro["autor"],
            "disponibilidade": livro["disponibilidade"]
        }
    else:
        return {
            "error_message": f"Livro '{nome_livro}' não encontrado no acervo."
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
        "Em seguida você irá buscar o livro no acervo e retornar a informação se o livro está disponível ou não"
        
    ),
    tools=[buscar_livro],
)