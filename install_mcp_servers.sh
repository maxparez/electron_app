#!/bin/bash
# install_mcp_servers.sh

echo "Instalace MCP serverů pro Electron App projekt..."

# Filesystem server
echo "1. Instalace Filesystem MCP..."
npm install -g @modelcontextprotocol/server-filesystem

# Git server
echo "2. Instalace Git MCP..."
npm install -g @modelcontextprotocol/server-git

# Context7
echo "3. Instalace Context7..."
npm install -g context7

# Fetch server
echo "4. Instalace Fetch MCP..."
npm install -g @modelcontextprotocol/server-fetch

echo "✅ Instalace dokončena!"
echo "Nezapomeňte nakonfigurovat claude_desktop_config.json"