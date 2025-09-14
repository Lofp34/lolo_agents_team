# src/mcp_re/main.py
import logging
import os
from pathlib import Path

from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

from mcp_re.crew import build_crew

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "mcp_re.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger("mcp_re.main")


def run():
    # Démo simple : on reste focus sur "Montpellier informatique"
    # Montpellier (code INSEE "code_commune") = 34172
    # Référence INSEE: 34172 pour Montpellier. 
    user_query = input("Requête simple (ville + secteur) [ex: Montpellier informatique] : ").strip()
    if not user_query:
        user_query = "Montpellier formation"

    # On "déduit" juste un cas démo : si "Montpellier" est présent -> code_commune 34172
    code_commune = "34172" if "montpellier" in user_query.lower() else None

    # Prépare le serveur MCP (STDIO) -> le package Node est exécuté en local via npx
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-recherche-entreprises"],
        env=os.environ,
    )

    logger.info("Démarrage MCP (STDIO) : %s %s", server_params.command, server_params.args)

    # PATTERN RECOMMANDÉ : ouvrir MCP et lancer tout le crew dans le même with
    with MCPServerAdapter(server_params) as mcp_tools:
        logger.info("Tools MCP disponibles: %s", [t.name for t in mcp_tools])

        crew = build_crew(mcp_tools)

        # Inputs pour la task : on passe la requête telle quelle
        inputs = {
            "query": user_query,
            # Optionnel : on peut injecter le code_commune pour aider le modèle
            # mais le prompt de la task explique déjà qu'il faut utiliser "code_commune".
            "code_commune": code_commune,
        }
        logger.info("Kickoff du crew avec inputs: %s", inputs)

        result = crew.kickoff(inputs=inputs)
        print("\n== Résultat ==\n")
        print(result)

    logger.info("Serveur MCP STDIO fermé proprement.")


if __name__ == "__main__":
    run()
