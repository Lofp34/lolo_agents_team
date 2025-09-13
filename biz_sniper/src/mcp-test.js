// src/mcp-test.js
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  // 1) Connexion au serveur MCP
  const transport = new StdioClientTransport({
    command: "npx",
    args: ["mcp-recherche-entreprises"],
  });

  const client = new Client({
    name: "biz-sniper-test",
    version: "1.0.0",
  });

  await client.connect(transport);
  console.log("✅ Connecté au serveur MCP.");

  // 2) Lister les outils
  const listed = await client.listTools();
  console.log("Outils disponibles :", listed);

  // 3) Appel avec critères
  const res = await client.callTool({
    name: "rechercher_entreprise",
    arguments: {
      q: "informatique",              // requis
      commune: "Lyon",                // filtre ville
      code_naf: "62.01Z",             // secteur d'activité
      tranche_effectif_salarie: "12", // 20-49 salariés
      page: 1,
      per_page: 10
    }
  });

  // 4) Affichage résultat
  const content = res?.content?.[0];
  let entreprises = [];
  if (content?.type === "json" && content.json) {
    entreprises = content.json;
  } else if (content?.type === "text" && content.text) {
    try { entreprises = JSON.parse(content.text); } catch { entreprises = []; }
  }

  console.log("Résultats :", entreprises);

  await transport.close?.();
}

main().catch(err => {
  console.error("Erreur agent:", err);
});
