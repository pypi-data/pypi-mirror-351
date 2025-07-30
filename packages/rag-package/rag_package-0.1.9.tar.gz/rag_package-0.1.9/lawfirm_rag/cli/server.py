"""
Server CLI module for RAG.

Handles the 'serve' command functionality for starting the web server.
"""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def start_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    api_key: Optional[str] = None,
    cors: bool = False,
    open_browser: bool = False,
    verbose: bool = False,
    config: Optional[str] = None
) -> None:
    """Start the RAG web server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        reload: Enable auto-reload for development
        api_key: API key for authentication
        cors: Enable CORS for web frontend
        open_browser: Automatically open browser to the web UI
        verbose: Enable verbose output
        config: Path to configuration file
    """
    try:
        import uvicorn
    except ImportError:
        console.print("[red]Error: uvicorn is required to run the server.[/red]")
        console.print("Install with: pip install uvicorn[standard]")
        sys.exit(1)
    
    from ..utils.config import ConfigManager
    
    # Load configuration
    config_manager = ConfigManager(config_path=config)
    config_data = config_manager.get_config()
    
    # Override config with CLI arguments
    server_config = config_data.get("api", {})
    if host != "127.0.0.1":
        server_config["host"] = host
    if port != 8000:
        server_config["port"] = port
    if cors:
        server_config["cors"] = True
    if api_key:
        server_config["api_key"] = api_key
    
    # Set environment variables for the FastAPI app
    import os
    if api_key:
        os.environ["LAWFIRM_RAG_API_KEY"] = api_key
    if cors:
        os.environ["LAWFIRM_RAG_CORS_ENABLED"] = "true"
    if verbose:
        os.environ["LAWFIRM_RAG_VERBOSE"] = "true"
    if config:
        os.environ["LAWFIRM_RAG_CONFIG_PATH"] = config
    
    console.print("🚀 [bold blue]Starting RAG Server[/bold blue]")
    console.print(f"   Host: [cyan]{host}[/cyan]")
    console.print(f"   Port: [cyan]{port}[/cyan]")
    
    if api_key:
        console.print("   [yellow]🔐 API key authentication enabled[/yellow]")
    if cors:
        console.print("   [yellow]🌐 CORS enabled[/yellow]")
    if reload:
        console.print("   [yellow]🔄 Auto-reload enabled (development mode)[/yellow]")
    
    console.print(f"\n✨ [bold green]Server starting...[/bold green]")
    console.print(f"   Web UI: [link]http://{host}:{port}[/link]")
    console.print(f"   API docs: [link]http://{host}:{port}/docs[/link]")
    
    if open_browser:
        try:
            import webbrowser
            import threading
            import time
            
            def open_browser_delayed():
                time.sleep(2)  # Wait for server to start
                webbrowser.open(f"http://{host}:{port}")
                
            threading.Thread(target=open_browser_delayed, daemon=True).start()
            console.print("   [dim]🌐 Opening browser automatically...[/dim]")
        except Exception:
            pass  # Silently fail if browser opening doesn't work
    
    console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")
    
    try:
        # Import the FastAPI app
        from ..api.fastapi_app import app
        
        # Configure uvicorn
        uvicorn_config = {
            "app": app,
            "host": host,
            "port": port,
            "reload": reload,
            "log_level": "debug" if verbose else "info",
        }
        
        # Start the server
        uvicorn.run(**uvicorn_config)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error starting server: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1) 