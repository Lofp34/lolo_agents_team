#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Approche MCP correcte avec CrewAI :
- Connexion au serveur MCP via Stdio (npx mcp-recherche-entreprises)
- Passage des tools MCP à l'Agent
- Les "hints" pour mapper la requête -> args du tool sont dans backstory/description
"""

# (Optionnel) calmer quelques warnings sous Py 3.13
import warnings
try:
    from pydantic.warnings import PydanticDeprecatedSince20
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
except Exception:
    warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"pydantic(\.|$)")
warnings.filterwarnings("ignore", message=r"There is no current event loop")

import os
from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

# 1) Connexion MCP (Stdio)
server_params = StdioServerParameters(
    command="npx",
    args=["mcp-recherche-entreprises"],
    env=os.environ
)

with MCPServerAdapter(server_params, connect_timeout=60) as mcp_tools:
    print("Tools MCP:", [t.name for t in mcp_tools])

    # 2) Agent : on met les consignes de mapping ici (pas dans Task.context)
    agent = Agent(
        role="Prospecteur d'entreprises",
        goal="Trouver des entreprises correspondant à des critères et livrer un résumé exploitable.",
        backstory=(
            "Tu sais utiliser des tools MCP et leurs schémas JSON. "
            "Quand on te demande ‘Montpellier · informatique · 50–250’, traduis ainsi : "
            "- Localisation Montpellier : privilégie code_commune=34172 ou les CP 34000,34070,34080,34090.\n"
            "- Secteur 'informatique' : NAF division 62 → 62.01Z,62.02A,62.02B,62.03Z,62.09Z (ou section J si pertinent).\n"
            "- Effectif 50–250 : tranche_effectif_salarie = 21,22,31 (≈50-99, 100-199, 200-499).\n"
            "- Respecte per_page<=25 ; 'include' uniquement si minimal=true."
        ),
        tools=mcp_tools,      # on met à dispo les tools exposés par le MCP
        verbose=True,
        reasoning=True
    )

    # 3) Task : on décrit la demande en NL ; l'agent choisit et appelle le tool
    task = Task(
        description=(
            "Trouve des entreprises à Perpignan dans le secteur de la formation professionnelle avec 50–250 collaborateurs. "
            "Utilise le tool MCP approprié, en traduisant les contraintes selon le schéma. "
            "Livrable : un tableau Markdown (max 15 lignes) — Colonnes : Nom | SIREN/SIRET | Ville | Code NAF | Tranche effectif — "
            "puis 3–4 lignes d’analyse (tendances, concentration géographique/NAF)."
        ),
        expected_output="Tableau Markdown + courte synthèse.",
        agent=agent,
        tools=list(mcp_tools)  # (facultatif) force l'usage des tools MCP pour cette tâche
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    print("\n===== RÉSULTAT =====\n")
    print(result)
