# src/mcp_re/crew.py
from crewai import Agent, Crew, Process, Task
import yaml
from pathlib import Path


def load_yaml(p: str):
    with open(Path(__file__).parent / "config" / p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_crew(mcp_tools):
    """
    Construit l'agent et la task en utilisant les tools MCP déjà ouverts.
    NE FERME PAS la connexion MCP ici.
    """
    agents_cfg = load_yaml("agents.yaml")
    tasks_cfg = load_yaml("tasks.yaml")

    # On peut filtrer si tu veux réduire aux seuls outils utiles :
    tool_names = {t.name for t in mcp_tools}
    # Par défaut, on passe tous les tools au cas où (ok aussi).
    tools_for_agent = [t for t in mcp_tools if t.name in tool_names]

    agent = Agent(
        role=agents_cfg["prospecteur"]["role"],
        goal=agents_cfg["prospecteur"]["goal"],
        backstory=agents_cfg["prospecteur"]["backstory"],
        allow_delegation=agents_cfg["prospecteur"].get("allow_delegation", False),
        verbose=agents_cfg["prospecteur"].get("verbose", True),
        tools=tools_for_agent,  # <-- Très important : tools MCP vivants
        reasoning=True,
    )

    task_cfg = tasks_cfg["simple_task"]
    task = Task(
        description=task_cfg["description"],
        expected_output=task_cfg["expected_output"],
        agent=agent,
        markdown=True,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    return crew
