#!/usr/bin/env python3

import asyncio
import logging
import os
import sys

from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

# Configurer logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("mcp_minimal_crew_test")


def ensure_event_loop():
    """S’assure qu’il y a une boucle d’événements active non fermée."""
    try:
        loop = asyncio.get_running_loop()
        if loop.is_closed():
            raise RuntimeError("Event loop is closed")
        logger.debug("Event loop OK")
    except RuntimeError:
        logger.debug("Création d’une nouvelle event loop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def build_crew(q: str, commune: str):
    ensure_event_loop()

    server_params = StdioServerParameters(
        command="npx",
        args=["mcp-recherche-entreprises"],
        env=os.environ,
    )

    with MCPServerAdapter(server_params) as mcp_tools:
        tool_names = [t.name for t in mcp_tools]
        logger.debug(f"Tools disponibles: {tool_names}")

        # On construit un agent qui a ces outils
        agent = Agent(
            role="Test Agent",
            goal=f"Faire une recherche MPC minimal pour {q} à {commune}",
            tools=mcp_tools,
            reasoning=True,
            verbose=True,
        )

        # Définir une tâche qui dit à l’agent de faire cette recherche
        # On passe user_query et dans le backstory / description, on force l’agent à utiliser q + commune
        task_description = f"Utilisateur: {q}, {commune}. Recherche d'entreprises simples."
        task = Task(
            description=task_description,
            expected_output="Liste simple d’entreprises",
            agent=agent
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        return crew

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        q = sys.argv[1]
        commune = sys.argv[2]
    else:
        q = "informatique"
        commune = "Montpellier"

    logger.info(f"Démarrage du test minimal avec q='{q}', commune='{commune}'")

    crew = build_crew(q, commune)
    result = crew.kickoff(inputs={"user_query": f"{q} {commune}"})
    logger.info("Resultat du crew :")
    print(result)
