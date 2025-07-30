import asyncio, json, sqlite3, os
from typing import List, Dict, Set, Optional, Tuple, Any
from contextlib import contextmanager

from rich.console import Console
from rich.table import Table

from . import MCPClient, MCPConfig

console = Console()

class MCPRegistryException(Exception):
    pass

@contextmanager
def get_db_connection():
    """Context manager for SQLite database connections"""
    # Get the directory where this Python file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, ".mcp_registry.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the SQLite database with required tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create mcps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mcps (
                name TEXT PRIMARY KEY,
                description TEXT,
                command TEXT,
                args TEXT,
                required_envs TEXT,
                needs_envs BOOLEAN,
                url TEXT,
                ws_url TEXT,
                headers TEXT,
                auth_token TEXT,
                tags TEXT,
                version TEXT
            )
        ''')
        
        # Create tool_index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_index (
                tool_name TEXT,
                mcp_name TEXT,
                PRIMARY KEY (tool_name, mcp_name),
                FOREIGN KEY (mcp_name) REFERENCES mcps (name) ON DELETE CASCADE
            )
        ''')
        
        # Create tag_index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tag_index (
                tag TEXT,
                mcp_name TEXT,
                PRIMARY KEY (tag, mcp_name),
                FOREIGN KEY (mcp_name) REFERENCES mcps (name) ON DELETE CASCADE
            )
        ''')
        
        # Create tool_cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_cache (
                mcp_name TEXT PRIMARY KEY,
                tools TEXT,
                FOREIGN KEY (mcp_name) REFERENCES mcps (name) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()

class MCPRegistry:
    """
    Registry for Model Context Protocol servers.
    Allows registering, searching, and managing MCP configurations.
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        """
        Implement singleton pattern
        """
        
        if cls._instance is None:
            cls._instance = super(MCPRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the registry if not already initialized
        """
        
        if self._initialized:
            return
            
        # Registry storage
        self._mcps: Dict[str, MCPConfig] = {}
        self._tools_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
                
        # Cache of tool availability per MCP
        self._tool_cache: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize database
        init_database()
        
        # Mark as initialized
        self._initialized = True
        
        # Load from database
        self._load_from_db()

    def _load_from_db(self) -> None:
        """
        Load registry data from database
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing data
                self._mcps.clear()
                self._tools_index.clear()
                self._tag_index.clear()
                self._tool_cache.clear()
                
                # Load MCPs
                cursor.execute('SELECT * FROM mcps')
                for row in cursor.fetchall():
                    # Convert row to MCPConfig
                    config_dict = {
                        "name": row["name"],
                        "description": row["description"] or "",
                        "command": row["command"] or "",
                        "args": json.loads(row["args"]) if row["args"] else [],
                        "required_envs": json.loads(row["required_envs"]) if row["required_envs"] else [],
                        "needs_envs": bool(row["needs_envs"]),
                        "url": row["url"] or "",
                        "ws_url": row["ws_url"] or "",
                        "headers": json.loads(row["headers"]) if row["headers"] else {},
                        "auth_token": row["auth_token"] or "",
                        "tags": json.loads(row["tags"]) if row["tags"] else [],
                        "version": row["version"] or ""
                    }
                    mcp_config = MCPConfig(**config_dict)
                    self._mcps[row["name"]] = mcp_config
                
                # Load tool index
                cursor.execute('SELECT tool_name, mcp_name FROM tool_index')
                for row in cursor.fetchall():
                    tool_name = row["tool_name"]
                    mcp_name = row["mcp_name"]
                    if tool_name not in self._tools_index:
                        self._tools_index[tool_name] = set()
                    self._tools_index[tool_name].add(mcp_name)
                
                # Load tag index
                cursor.execute('SELECT tag, mcp_name FROM tag_index')
                for row in cursor.fetchall():
                    tag = row["tag"]
                    mcp_name = row["mcp_name"]
                    if tag not in self._tag_index:
                        self._tag_index[tag] = set()
                    self._tag_index[tag].add(mcp_name)
                
                # Load tool cache
                cursor.execute('SELECT mcp_name, tools FROM tool_cache')
                for row in cursor.fetchall():
                    tools_data = json.loads(row["tools"]) if row["tools"] else []
                    self._tool_cache[row["mcp_name"]] = tools_data
                
                console.print(f"[green]Loaded {len(self._mcps)} MCPs from local SQLite database[/green]")
        
        except Exception as e:
            console.print(f"[red]Failed to load MCP registry from database: {str(e)}[/red]")
            raise MCPRegistryException(f"Failed to load MCP registry from database: {str(e)}")
    
    def _save_to_db(self) -> None:
        """
        Persist registry data to database
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Begin transaction
                cursor.execute("BEGIN")
                
                # For each MCP, insert or update
                for name, config in self._mcps.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO mcps (
                            name, description, command, args, required_envs, 
                            needs_envs, url, ws_url, headers, auth_token, tags, version
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        name, config.description, config.command, 
                        json.dumps(config.args), json.dumps(config.required_envs),
                        config.needs_envs, config.url, config.ws_url, 
                        json.dumps(config.headers), config.auth_token, 
                        json.dumps(config.tags), config.version
                    ))
                
                # Clear and repopulate tool index
                cursor.execute("DELETE FROM tool_index")
                for tool, mcp_names in self._tools_index.items():
                    for mcp_name in mcp_names:
                        cursor.execute('''
                            INSERT INTO tool_index (tool_name, mcp_name)
                            VALUES (?, ?)
                        ''', (tool, mcp_name))
                
                # Clear and repopulate tag index
                cursor.execute("DELETE FROM tag_index")
                for tag, mcp_names in self._tag_index.items():
                    for mcp_name in mcp_names:
                        cursor.execute('''
                            INSERT INTO tag_index (tag, mcp_name)
                            VALUES (?, ?)
                        ''', (tag, mcp_name))
                
                # Update tool cache
                cursor.execute("DELETE FROM tool_cache")
                for mcp_name, tools in self._tool_cache.items():
                    cursor.execute('''
                        INSERT INTO tool_cache (mcp_name, tools)
                        VALUES (?, ?)
                    ''', (mcp_name, json.dumps(tools)))
                
                # Commit transaction
                conn.commit()
                
        except Exception as e:
            console.print(f"[red]Failed to save MCP registry to database: {str(e)}[/red]")
            raise MCPRegistryException(f"Failed to save MCP registry to database: {str(e)}")
        
    def test_connection(
            self, 
            mcp_config: MCPConfig
        ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Test connection to an MCP server and retrieve its tools
        
        Args:
            mcp_config: The MCP configuration to test
            
        Returns:
            Tuple of (success, message, tools)
        """
        try:
            tools = self._discover_mcp_tools(mcp_config)
            tool_names = [tool.get("name") for tool in tools]
            return True, f"Successfully connected. Found {len(tools)} tools: {', '.join(tool_names)}", tools
        except Exception as e:
            return False, f"Connection test failed: {str(e)}", []
    
    def register(
            self, 
            mcp_config: MCPConfig
        ) -> bool:
        """
        Register an MCP configuration in the registry and automatically discover its tools
        Only registers if connection test succeeds.
        If the MCP is already registered, it will be updated.
        
        Args:
            mcp_config: The MCP configuration to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        if not isinstance(mcp_config, MCPConfig):
            raise MCPRegistryException("mcp_config must be an instance of MCPConfig")
            
        name = mcp_config.name
        
        # First test the connection before registering
        try:
            # Test connection and discover tools
            success, message, tools = self.test_connection(mcp_config)
            
            if success:
                # Create a clean version to store in the registry
                clean_config = MCPConfig(
                    name=mcp_config.name,
                    description=mcp_config.description,
                    command=mcp_config.command,
                    args=mcp_config.args.copy() if mcp_config.args else [],
                    required_envs=mcp_config.required_envs,
                    needs_envs=mcp_config.needs_envs,
                    url=mcp_config.url,
                    ws_url=mcp_config.ws_url,
                    headers=mcp_config.headers.copy() if mcp_config.headers else {},
                    auth_token=mcp_config.auth_token,
                    tags=mcp_config.tags.copy() if mcp_config.tags else [],
                    version=mcp_config.version
                )

                # Register the clean version instead of the original
                self._mcps[name] = clean_config
                
                # Index by tags
                for tag in mcp_config.tags:
                    if tag not in self._tag_index:
                        self._tag_index[tag] = set()
                    self._tag_index[tag].add(name)
                
                # Store complete tool information
                self._tool_cache[name] = tools
                
                # Update tools index with tool names
                for tool in tools:
                    tool_name = tool.get("name")
                    if tool_name:
                        if tool_name not in self._tools_index:
                            self._tools_index[tool_name] = set()
                        self._tools_index[tool_name].add(name)
                
                # Persist changes
                self._save_to_db()
                
                console.print(f"[green]Successfully registered {name} with {len(tools)} tools[/green]")
                return True
            else:
                console.print(f"[red]Failed to register {name}: {message}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Failed to register {name}: {e}[/red]")
            return False
    
    def unregister(
            self, 
            name: str
        ) -> bool:
        """
        Remove an MCP configuration from the registry
        
        Args:
            name: Name of the MCP to unregister
            
        Returns:
            True if unregistration was successful
        """
        if name not in self._mcps:
            return False
        
        # Remove from main dictionary
        del self._mcps[name]
        
        # Remove from tools index
        for tool_name, mcp_names in self._tools_index.items():
            if name in mcp_names:
                mcp_names.remove(name)
                
        # Remove from tag index
        for tag, mcp_names in self._tag_index.items():
            if name in mcp_names:
                mcp_names.remove(name)
        
        # Remove from tool cache
        if name in self._tool_cache:
            del self._tool_cache[name]
        
        # Persist changes
        self._save_to_db()
        
        return True
    
    def get_by_name(
            self, 
            name: str
        ) -> Optional[MCPConfig]:
        """
        Get an MCP configuration by name
        
        Args:
            name: Name of the MCP to retrieve
            
        Returns:
            MCPConfig if found, None otherwise
        """
        return self._mcps.get(name)
    
    def search_by_tool(
            self, 
            tool_name: str
        ) -> List[MCPConfig]:
        """
        Find all MCPs that provide a specific tool
        
        Args:
            tool_name: Name of the tool to search for
            
        Returns:
            List of MCPConfig objects that provide the tool
        """
        if tool_name not in self._tools_index:
            return []
            
        return [self._mcps[name] for name in self._tools_index[tool_name] if name in self._mcps]
    
    def search_by_tag(
            self, 
            tag: str
        ) -> List[MCPConfig]:
        """
        Find all MCPs with a specific tag
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of MCPConfig objects with the specified tag
        """
        if tag not in self._tag_index:
            return []
            
        return [self._mcps[name] for name in self._tag_index[tag] if name in self._mcps]
    
    def search_by_description(
        self, 
        query: str,
        fuzzy: bool = True
    ) -> List[MCPConfig]:
        """
        Find all MCPs whose descriptions contain the given query
        
        Args:
            query: Text to search for in descriptions
            fuzzy: If True, use case-insensitive partial matching
                
        Returns:
            List of MCPConfig objects matching the description search
        """
        results = []
        
        if not query:
            return results
            
        query = query.lower() if fuzzy else query
        
        for name, config in self._mcps.items():
            description = config.description
            if fuzzy:
                description = description.lower()
                
            if query in description:
                results.append(config)
                
        return results

    def search(
            self, 
            query: str,
            fuzzy: bool = True
        ) -> List[MCPConfig]:
        """
        Universal search across names, descriptions, tags, and tools
        
        Args:
            query: Text to search for across all fields
            fuzzy: If True, use case-insensitive partial matching
                
        Returns:
            List of MCPConfig objects matching the search
        """
        if not query:
            return []
            
        query = query.lower() if fuzzy else query
        results = set()
        
        # Search in names
        for name, config in self._mcps.items():
            name_to_check = name.lower() if fuzzy else name
            if query in name_to_check:
                results.add(name)
        
        # Search in descriptions
        for name, config in self._mcps.items():
            description = config.description.lower() if fuzzy else config.description
            if query in description:
                results.add(name)
        
        # Search in tags
        for name, config in self._mcps.items():
            for tag in config.tags:
                tag_to_check = tag.lower() if fuzzy else tag
                if query in tag_to_check:
                    results.add(name)
                    break
        
        # Search in tools
        for tool_name, mcp_names in self._tools_index.items():
            tool_to_check = tool_name.lower() if fuzzy else tool_name
            if query in tool_to_check:
                results.update(mcp_names)
        
        # Convert set of names to list of configs
        return [self._mcps[name] for name in results if name in self._mcps]
    
    def list_all(self) -> List[MCPConfig]:
        """
        List all registered MCPs
        
        Returns:
            List of all registered MCPConfig objects
        """
        return list(self._mcps.values())
    
    def get_tools_for_mcp(
            self, 
            name: str
        ) -> List[Dict[str, Any]]:
        """
        Get the list of tools provided by an MCP
        
        Args:
            name: Name of the MCP
            
        Returns:
            List of tool information dictionaries
        """
        if name not in self._mcps:
            raise MCPRegistryException(f"MCP '{name}' not found in registry")
            
        # Return from cache if available
        if name in self._tool_cache:
            return self._tool_cache[name]
            
        # Try to discover tools
        try:
            success, message, tools = self.test_connection(self._mcps[name])
            
            if not success:
                raise MCPRegistryException(message)
                
            # Cache the discovered tools
            self._tool_cache[name] = tools
            
            # Update tools index
            for tool in tools:
                tool_name = tool.get("name")
                if tool_name:
                    if tool_name not in self._tools_index:
                        self._tools_index[tool_name] = set()
                    self._tools_index[tool_name].add(name)
                
            # Persist changes
            self._save_to_db()
            
            return tools
        except Exception as e:
            raise MCPRegistryException(f"Failed to discover tools for MCP '{name}': {e}")
    
    def _discover_mcp_tools(
            self, 
            mcp_config: MCPConfig
        ) -> List[Dict[str, Any]]:
        """
        Connect to an MCP and discover its tools
        
        Args:
            mcp_config: Configuration for the MCP
            
        Returns:
            List of tool information dictionaries
        """
        try:
            # Create event loop if needed
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            tools_data = []
            
            def discover_tools():
                with MCPClient(config=mcp_config) as client:
                    discovered_tools = client.discover_tools()
                    return discovered_tools
            
            # Run the discovery process with a timeout
            discovered_tools = loop.run_until_complete(
                asyncio.wait_for(
                    asyncio.to_thread(discover_tools),
                    timeout=30.0
                )
            )
            
            # Convert Tool objects to serializable dictionaries
            for tool in discovered_tools:
                tool_dict = {
                    "name": tool.name,
                    "description": getattr(tool, "description", ""),
                    "inputSchema": getattr(tool, "inputSchema", {}),
                    "annotations": getattr(tool, "annotations", None)
                }
                tools_data.append(tool_dict)
            
            return tools_data
            
        except Exception as e:
            raise MCPRegistryException(f"Failed to discover tools: {e}")
    
    def __repr__(self):
        """
        Print the registry contents in a formatted table
        
        Args:
            show_tools: Whether to include tools in the output
        """
        table = Table(title="MCP Registry")
        
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Type", style="green")
        
        table.add_column("Tools", style="yellow")
        
        for name, config in self._mcps.items():
            # Determine connector type for display
            if hasattr(config, 'TYPE_STDIO') and config.TYPE_STDIO:
                connector_type = "stdio"
            elif hasattr(config, 'TYPE_HTTP') and config.TYPE_HTTP:
                connector_type = "http"
            elif hasattr(config, 'TYPE_WEBSOCKET') and config.TYPE_WEBSOCKET:
                connector_type = "websocket"
            elif config.command:
                connector_type = "stdio"
            elif config.url:
                connector_type = "http"
            elif config.ws_url:
                connector_type = "websocket"
            else:
                connector_type = "unknown"
                
            if name in self._tool_cache:
                tool_names = [tool.get("name", "") for tool in self._tool_cache[name] if tool.get("name")]
                tools_str = ", ".join(tool_names) if tool_names else "[dim]no tools[/dim]"
            else:
                tools_str = "[dim]unknown[/dim]"
                
            table.add_row(name, config.description, connector_type, tools_str)
        
        console.print(table)
        return ""