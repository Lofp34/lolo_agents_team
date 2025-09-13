"""
Adaptateur MCP local pour remplacer MCPServerAdapter manquant dans crewai_tools.
Convertit les outils MCP en outils CrewAI compatibles.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from crewai.tools import BaseTool
from mcp import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession
from mcp.types import Tool, CallToolResult
from pydantic import BaseModel, Field, create_model


class MCPTool(BaseTool):
    """Outil CrewAI qui encapsule un outil MCP."""
    
    def __init__(self, mcp_tool: Tool, session: ClientSession):
        self.mcp_tool = mcp_tool
        self.session = session
        
        # Créer le schéma d'arguments à partir du inputSchema MCP
        args_schema = self._create_args_schema(mcp_tool.inputSchema)
        
        super().__init__(
            name=mcp_tool.name,
            description=mcp_tool.description or f"Outil MCP: {mcp_tool.name}",
            args_schema=args_schema
        )
    
    def _create_args_schema(self, input_schema: Dict[str, Any]) -> type[BaseModel]:
        """Convertit le JSON Schema MCP en schéma Pydantic."""
        if not input_schema or "properties" not in input_schema:
            # Schéma vide si pas de propriétés
            return create_model(f"{self.mcp_tool.name}Schema", __base__=BaseModel)
        
        fields = {}
        for prop_name, prop_def in input_schema["properties"].items():
            # Déterminer le type Python à partir du type JSON Schema
            json_type = prop_def.get("type", "string")
            python_type = self._json_type_to_python(json_type)
            
            # Créer le champ Pydantic
            field_info = Field(
                description=prop_def.get("description", ""),
                default=... if prop_name in input_schema.get("required", []) else None
            )
            fields[prop_name] = (python_type, field_info)
        
        return create_model(f"{self.mcp_tool.name}Schema", **fields)
    
    def _json_type_to_python(self, json_type: str) -> type:
        """Convertit un type JSON Schema en type Python."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        return type_mapping.get(json_type, str)
    
    def _run(self, **kwargs) -> Any:
        """Exécute l'outil MCP de manière synchrone."""
        # Nettoyer les arguments None
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        # Exécuter l'appel MCP de manière asynchrone
        return asyncio.run(self._async_call_tool(clean_kwargs))
    
    async def _async_call_tool(self, arguments: Dict[str, Any]) -> Any:
        """Appelle l'outil MCP de manière asynchrone."""
        try:
            result: CallToolResult = await self.session.call_tool(self.mcp_tool.name, arguments)
            
            # Extraire le contenu textuel du résultat
            if result.content:
                text_parts = []
                for content_block in result.content:
                    if hasattr(content_block, 'text'):
                        text_parts.append(content_block.text)
                    elif isinstance(content_block, dict) and content_block.get('type') == 'text':
                        text_parts.append(content_block.get('text', ''))
                
                if text_parts:
                    return '\n'.join(text_parts)
            
            # Si pas de contenu textuel, retourner le contenu structuré
            if result.structuredContent:
                return json.dumps(result.structuredContent, indent=2, ensure_ascii=False)
            
            return "Aucun résultat retourné par l'outil MCP"
            
        except Exception as e:
            return f"Erreur lors de l'appel de l'outil MCP {self.mcp_tool.name}: {str(e)}"


class MCPServerAdapter:
    """Adaptateur pour connecter un serveur MCP et exposer ses outils comme outils CrewAI."""
    
    def __init__(self, server_params: StdioServerParameters, connect_timeout: int = 30):
        self.server_params = server_params
        self.connect_timeout = connect_timeout
        self.session: Optional[ClientSession] = None
        self.tools: List[MCPTool] = []
    
    async def __aenter__(self):
        """Contexte asynchrone pour initialiser la connexion."""
        await self._connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage lors de la sortie du contexte."""
        await self._disconnect()
    
    def __enter__(self):
        """Contexte synchrone pour compatibilité avec le code existant."""
        # Créer un nouvel event loop si nécessaire
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Exécuter la connexion de manière synchrone
        loop.run_until_complete(self._connect())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage lors de la sortie du contexte synchrone."""
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._disconnect())
        except RuntimeError:
            pass
    
    async def _connect(self):
        """Établit la connexion avec le serveur MCP."""
        try:
            # Créer le client stdio
            async with stdio_client(self.server_params) as (read, write):
                # Créer la session client
                self.session = ClientSession(read, write)
                
                # Initialiser la session
                await self.session.initialize()
                
                # Lister les outils disponibles
                tools_result = await self.session.list_tools()
                
                # Créer les outils CrewAI
                self.tools = []
                for mcp_tool in tools_result.tools:
                    crewai_tool = MCPTool(mcp_tool, self.session)
                    self.tools.append(crewai_tool)
                
                print(f"Connecté au serveur MCP avec {len(self.tools)} outils disponibles")
                
        except Exception as e:
            print(f"Erreur lors de la connexion au serveur MCP: {e}")
            raise
    
    async def _disconnect(self):
        """Ferme la connexion avec le serveur MCP."""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                print(f"Erreur lors de la fermeture de la session MCP: {e}")
            finally:
                self.session = None
    
    def stop(self):
        """Méthode pour arrêter l'adaptateur (compatibilité avec l'API attendue)."""
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._disconnect())
        except RuntimeError:
            pass
    
    def filter_by_names(self, tool_names: Optional[List[str]] = None) -> List[MCPTool]:
        """Filtre les outils par nom (compatibilité avec l'API attendue)."""
        if tool_names is None:
            return self.tools
        
        return [tool for tool in self.tools if tool.name in tool_names]
    
    def __iter__(self):
        """Permet l'itération sur les outils."""
        return iter(self.tools)
    
    def __getitem__(self, index):
        """Permet l'accès par index aux outils."""
        return self.tools[index]
    
    def __len__(self):
        """Retourne le nombre d'outils."""
        return len(self.tools)
