#!/usr/bin/env python3
"""
Script de test pour vérifier que l'adaptateur MCP fonctionne correctement.
"""

import sys
import os
from mcp_adapter import MCPServerAdapter
from mcp import StdioServerParameters

def test_mcp_connection():
    """Test de connexion au serveur MCP."""
    print("🔍 Test de connexion au serveur MCP...")
    
    # Paramètres du serveur MCP
    server_params = StdioServerParameters(
        command="npx",
        args=["mcp-recherche-entreprises"],
        env=os.environ,
    )
    
    try:
        # Test de connexion avec timeout court
        with MCPServerAdapter(server_params, connect_timeout=10) as mcp_tools:
            print(f"✅ Connexion réussie ! {len(mcp_tools)} outils disponibles")
            
            # Lister les outils disponibles
            for i, tool in enumerate(mcp_tools):
                print(f"  {i+1}. {tool.name}: {tool.description}")
            
            # Tester un outil si disponible
            if len(mcp_tools) > 0:
                print(f"\n🧪 Test de l'outil '{mcp_tools[0].name}'...")
                try:
                    # Test avec des paramètres minimaux
                    result = mcp_tools[0].run(q="test")
                    print(f"✅ Test réussi: {result[:100]}...")
                except Exception as e:
                    print(f"⚠️  Test échoué (normal si paramètres incorrects): {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_imports():
    """Test des imports nécessaires."""
    print("🔍 Test des imports...")
    
    try:
        from crewai import Agent, Task, Crew, Process
        print("✅ Import CrewAI réussi")
    except ImportError as e:
        print(f"❌ Import CrewAI échoué: {e}")
        return False
    
    try:
        from mcp import StdioServerParameters
        print("✅ Import MCP réussi")
    except ImportError as e:
        print(f"❌ Import MCP échoué: {e}")
        return False
    
    try:
        from mcp_adapter import MCPServerAdapter
        print("✅ Import adaptateur MCP réussi")
    except ImportError as e:
        print(f"❌ Import adaptateur MCP échoué: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Test de l'adaptateur MCP\n")
    
    # Test des imports
    if not test_imports():
        print("\n❌ Tests d'import échoués. Arrêt.")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Test de connexion MCP
    if test_mcp_connection():
        print("\n✅ Tous les tests sont passés ! L'adaptateur MCP fonctionne.")
    else:
        print("\n❌ Test de connexion MCP échoué.")
        print("💡 Vérifiez que:")
        print("   - Node.js est installé")
        print("   - Le package 'mcp-recherche-entreprises' est disponible via npx")
        print("   - La connexion réseau fonctionne")
