from crewai import Agent, Task, Crew, Process
from mcp_adapter import MCPServerAdapter
from mcp import StdioServerParameters
import os

# 1) Connecter le serveur MCP (via npx)
server_params = StdioServerParameters(
    command="npx",
    args=["mcp-recherche-entreprises"],
    env=os.environ,  # Node doit être disponible dans le PATH
)

with MCPServerAdapter(server_params, connect_timeout=60) as mcp_tools:
    # (Optionnel) ne garder que les 2 outils utiles
    tools = [t for t in mcp_tools
             if t.name in ("rechercher_entreprise", "rechercher_entreprise_geographiques")]

    # 2) Agent qui sait utiliser les tools à partir d'une requête NL
    agent = Agent(
        role="Prospecteur d'entreprises",
        goal=("Trouver des entreprises françaises selon des critères exprimés en langage naturel "
              "et retourner une liste exploitable pour la prospection."),
        backstory=(
            "Tu utilises les outils MCP disponibles. "
            "Quand l'utilisateur demande un secteur et une ville, appelle l'outil "
            "'rechercher_entreprise' avec ces paramètres.\n"
            "- Le paramètre 'q' est OBLIGATOIRE : mets un mot-clé pertinent (ex: secteur ou 'entreprise').\n"
            "- 'commune' pour la ville (ex: 'Montpellier').\n"
            "- 'code_naf' si le secteur est connu (ex: '62.01Z' pour Programmation informatique), "
            "sinon un mot-clé dans 'q'.\n"
            "- 'tranche_effectif_salarie' filtre par effectif. Si l'utilisateur donne une FOURCHETTE qui "
            "couvre plusieurs tranches SIRENE, fais plusieurs appels et fusionne les résultats (clé: siren).\n"
            "Codes tranches utiles: '12'=20-49, '21'=50-99, '22'=100-199, '31'=200-249.\n"
            "Déduplique par 'siren'. Retourne un tableau concis: denomination, siren, siret, naf, commune, tranche."
        ),
        tools=tools,
        reasoning=True,
        verbose=True,
    )

    # 3) Task: on passe la requête telle quelle — l'agent choisit les bons appels MCP
    task = Task(
        description=(
            "Utilisateur: {user_query}\n"
            "Objectif: trouver jusqu'à 50 entreprises correspondant à la demande, "
            "en appelant les outils MCP si nécessaire. "
            "Si la fourchette d'effectif est 20–250, couvre les tranches '12','21','22','31' "
            "au besoin et fusionne/déduplique."
        ),
        expected_output="Un tableau Markdown (max 50 lignes) avec denomination, siren, siret, naf, commune, tranche.",
        agent=agent,
        markdown=True,
        human_input=False,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={
        "user_query": "entreprises du secteur informatique sur Montpellier entre 20 et 250 collaborateurs"
    })
    print(result)
