"""
Main CLI entry point for LawFirm-RAG package.

Provides command-line interface for document analysis, query generation,
and server management with automatic virtual environment management.
"""

import sys
import os
import click
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .. import __version__
from .env_manager import EnvironmentManager, get_rag_env_path, is_in_rag_env, find_rag_environment

console = Console()


def check_dependencies():
    """Check if critical dependencies are installed."""
    missing_deps = []
    
    try:
        import torch
    except ImportError:
        missing_deps.append("torch")
    
    try:
        import sentence_transformers
    except ImportError:
        missing_deps.append("sentence-transformers")
    
    try:
        import chromadb
    except ImportError:
        missing_deps.append("chromadb")
    
    if missing_deps:
        console.print(f"[red]❌ Missing critical dependencies: {', '.join(missing_deps)}[/red]")
        console.print("[yellow]Try running setup first:[/yellow]")
        console.print("[cyan]rag setup[/cyan]")
        return False
    
    return True


def auto_use_rag_environment() -> bool:
    """Automatically use the RAG environment if it exists."""
    if is_in_rag_env():
        return True  # Already in RAG environment
    
    # Find any existing RAG environment
    rag_env_path = find_rag_environment()
    if not rag_env_path:
        return False  # No RAG environment found
    
    # Set environment variables to use the RAG environment
    if sys.platform == "win32":
        scripts_dir = rag_env_path / "Scripts"
        python_exe = scripts_dir / "python.exe"
        site_packages = rag_env_path / "Lib" / "site-packages"
    else:
        scripts_dir = rag_env_path / "bin"
        python_exe = scripts_dir / "python"
        site_packages = rag_env_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    
    if not python_exe.exists():
        return False
    
    # Update PATH and VIRTUAL_ENV for this session
    os.environ["VIRTUAL_ENV"] = str(rag_env_path)
    os.environ["PATH"] = f"{scripts_dir}{os.pathsep}{os.environ['PATH']}"
    os.environ.pop("PYTHONHOME", None)
    
    # CRITICAL: Update Python's import path to use the virtual environment
    if site_packages.exists():
        # Remove any existing site-packages from sys.path to avoid conflicts
        sys.path = [p for p in sys.path if "site-packages" not in p]
        # Add virtual environment's site-packages to the front
        sys.path.insert(0, str(site_packages))
    
    console.print(f"[green]🚀 Auto-using RAG environment: {rag_env_path}[/green]")
    return True


def ensure_environment() -> bool:
    """Ensure we're running in the RAG environment or guide user to setup."""
    # Try to auto-use existing environment
    if auto_use_rag_environment():
        return True
    
    console.print("[yellow]⚠️  RAG environment not found.[/yellow]")
    console.print("[cyan]Run this to set up:[/cyan]")
    console.print("[green]rag setup[/green]")
    return False


def check_python_version():
    """Check if Python version meets requirements."""
    if sys.version_info < (3, 11):
        console.print(f"[red]❌ Python {sys.version_info.major}.{sys.version_info.minor} is not supported[/red]")
        console.print("[yellow]RAG requires Python 3.11 or higher[/yellow]")
        console.print("\n[cyan]Installation guide for multiple Python versions:[/cyan]")
        console.print("[green]Windows:[/green] py -3.11 -m pip install rag-package")
        console.print("[green]macOS/Linux:[/green] python3.11 -m pip install rag-package")
        return False
    return True


@click.group()
@click.version_option(version=__version__, prog_name="rag")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--skip-checks", is_flag=True, help="Skip dependency checks")
@click.option("--skip-env-check", is_flag=True, help="Skip environment checks (for setup command)")
@click.pass_context
def main(ctx: click.Context, verbose: bool, config: Optional[str], skip_checks: bool, skip_env_check: bool) -> None:
    """
    RAG: AI-Powered Legal Document Analysis Package
    
    A modern Python package for legal document analysis, query generation,
    and AI-powered legal research assistance.
    
    🚀 Quick Start:
    rag setup          # Set up isolated environment (first time)
    rag serve          # Start the web UI
    rag analyze file   # Analyze a document
    rag query file     # Generate search queries
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config
    ctx.obj["skip_checks"] = skip_checks
    ctx.obj["skip_env_check"] = skip_env_check
    
    # Skip all checks for setup command
    if ctx.invoked_subcommand == "setup":
        return
    
    # Check Python version first
    if not check_python_version():
        sys.exit(1)
    
    # Check environment unless skipped
    if not skip_env_check and not ensure_environment():
        sys.exit(1)
    
    # Check dependencies unless skipped
    if not skip_checks and not check_dependencies():
        sys.exit(1)
    
    if verbose:
        console.print(f"[green]RAG v{__version__}[/green]")
        console.print(f"[dim]Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}[/dim]")
        if config:
            console.print(f"[blue]Using config: {config}[/blue]")


@main.command()
@click.option("--force", is_flag=True, help="Force recreation of existing environment")
@click.option("--activate", is_flag=True, help="Activate environment after setup")
@click.option("--remove", is_flag=True, help="Remove existing environment")
@click.option("--verify", is_flag=True, help="Verify existing environment")
@click.option("--repair", is_flag=True, help="Repair existing environment by reinstalling dependencies")
@click.pass_context
def setup(ctx: click.Context, force: bool, activate: bool, remove: bool, verify: bool, repair: bool) -> None:
    """
    🔧 Set up the RAG environment with all AI/ML dependencies.
    
    Creates an isolated virtual environment to ensure compatibility
    and prevent conflicts with other Python packages.
    
    Examples:
      rag setup                # Create environment
      rag setup --force        # Recreate environment  
      rag setup --activate     # Activate existing environment
      rag setup --verify       # Check environment status
      rag setup --repair       # Fix existing environment
      rag setup --remove       # Remove environment
    """
    from .env_manager import EnvironmentManager
    
    env_manager = EnvironmentManager()
    
    try:
        if remove:
            if env_manager.remove_environment():
                console.print("[green]✅ Environment removed successfully[/green]")
            sys.exit(0)
        
        if verify:
            if env_manager.verify_installation():
                console.print("[green]✅ Environment verified successfully[/green]")
            else:
                console.print("[red]❌ Environment verification failed[/red]")
                sys.exit(1)
            sys.exit(0)
        
        if activate:
            if env_manager.activate_environment():
                console.print("[green]✅ Environment activated[/green]")
            else:
                sys.exit(1)
            sys.exit(0)
        
        if repair:
            if env_manager.repair_environment():
                console.print("[green]✅ Environment repaired successfully[/green]")
            else:
                console.print("[red]❌ Environment repair failed[/red]")
                sys.exit(1)
            sys.exit(0)
        
        # Default: setup environment
        if env_manager.setup_complete_environment(force=force):
            console.print("[green]🎉 Setup completed successfully![/green]")
            
            if activate:
                env_manager.activate_environment()
        else:
            console.print("[red]❌ Setup failed[/red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Setup error: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "text"]), 
              default="text", help="Output format")
@click.option("--analysis-type", "-t", 
              type=click.Choice(["summary", "key_points", "legal_issues"]),
              default="summary", help="Type of analysis to perform")
@click.option("--recursive", "-r", is_flag=True, help="Process directories recursively")
@click.pass_context
def analyze(ctx: click.Context, files: tuple, output: Optional[str], 
           format: str, analysis_type: str, recursive: bool) -> None:
    """Analyze legal documents and extract insights."""
    from .analyze import analyze_documents
    
    try:
        analyze_documents(
            files=files,
            output=output,
            format=format,
            analysis_type=analysis_type,
            recursive=recursive,
            verbose=ctx.obj.get("verbose", False),
            config=ctx.obj.get("config")
        )
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--database", "-d", 
              type=click.Choice(["westlaw", "lexisnexis", "casetext"]),
              default="westlaw", help="Target legal database")
@click.option("--all-databases", is_flag=True, 
              help="Generate queries for all supported databases")
@click.option("--output", "-o", type=click.Path(), help="Output file for queries")
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "text"]),
              default="text", help="Output format")
@click.pass_context
def query(ctx: click.Context, files: tuple, database: str, all_databases: bool,
          output: Optional[str], format: str) -> None:
    """Generate search queries for legal databases."""
    from .query import generate_queries
    
    try:
        generate_queries(
            files=files,
            database=database,
            all_databases=all_databases,
            output=output,
            format=format,
            verbose=ctx.obj.get("verbose", False),
            config=ctx.obj.get("config")
        )
    except Exception as e:
        console.print(f"[red]Error generating queries: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@main.command()
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind the server to")
@click.option("--port", "-p", default=8000, type=int, help="Port to bind the server to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option("--api-key", type=str, help="API key for authentication")
@click.option("--cors", is_flag=True, help="Enable CORS for web frontend")
@click.option("--open-browser", is_flag=True, default=True, help="Automatically open browser (default: true)")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool, 
          api_key: Optional[str], cors: bool, open_browser: bool, no_browser: bool) -> None:
    """
    🚀 Start the RAG web server with a beautiful UI.
    
    This starts the FastAPI server with the web interface for AI-powered
    legal document analysis, query generation, and research assistance.
    
    Note: Requires proper environment setup. If this is your first time,
    run 'rag setup' to create an isolated environment with all dependencies.
    
    Examples:
      rag serve                    # Start on localhost:8000
      rag serve --port 3000        # Start on port 3000  
      rag serve --host 0.0.0.0     # Allow external connections
      rag serve --no-browser       # Don't open browser automatically
    """
    from .server import start_server
    
    # Double-check environment before starting server
    if not is_in_rag_env():
        console.print("[yellow]⚠️  Not running in RAG environment.[/yellow]")
        console.print("[cyan]For best performance, use the isolated environment:[/cyan]")
        console.print("[green]rag setup --activate[/green]")
        console.print("[dim]Or continue anyway...[/dim]")
    
    # Handle browser opening logic
    should_open_browser = open_browser and not no_browser
    
    try:
        start_server(
            host=host,
            port=port,
            reload=reload,
            api_key=api_key,
            cors=cors,
            open_browser=should_open_browser,
            verbose=ctx.obj.get("verbose", False),
            config=ctx.obj.get("config")
        )
    except Exception as e:
        console.print(f"[red]❌ Error starting server: {e}[/red]")
        if "No module named" in str(e) or "ImportError" in str(e):
            console.print("\n[yellow]🔧 This looks like a dependency issue.[/yellow]")
            console.print("[cyan]Try setting up the environment:[/cyan]")
            console.print("[green]rag setup[/green]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@main.group()
def models() -> None:
    """Manage AI models."""
    pass


@models.command("list")
@click.option("--available", is_flag=True, help="Show available models for download")
@click.pass_context
def list_models(ctx: click.Context, available: bool) -> None:
    """List installed or available AI models."""
    from ..models.model_manager import ModelManager
    
    try:
        manager = ModelManager()
        
        if available:
            console.print("[bold blue]Available Models for Download:[/bold blue]")
            models = manager.list_available_models()
        else:
            console.print("[bold blue]Installed Models:[/bold blue]")
            models = manager.list_installed_models()
        
        if not models:
            console.print("[yellow]No models found.[/yellow]")
            return
            
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Description", style="white")
        
        for model in models:
            table.add_row(
                model.get("name", "Unknown"),
                model.get("size", "Unknown"),
                model.get("description", "No description")
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing models: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@models.command("download")
@click.argument("model_name", required=False)
@click.option("--force", is_flag=True, help="Force re-download if model exists")
@click.pass_context
def download_model(ctx: click.Context, model_name: Optional[str], force: bool) -> None:
    """Download an AI model."""
    from ..models.model_manager import ModelManager
    
    try:
        manager = ModelManager()
        
        if not model_name:
            # Show available models and prompt for selection
            available = manager.list_available_models()
            if not available:
                console.print("[red]No models available for download.[/red]")
                return
                
            console.print("[bold blue]Available Models:[/bold blue]")
            for i, model in enumerate(available, 1):
                console.print(f"{i}. {model['name']} - {model['description']}")
                
            choice = click.prompt("Select a model number", type=int)
            if 1 <= choice <= len(available):
                model_name = available[choice - 1]["name"]
            else:
                console.print("[red]Invalid selection.[/red]")
                return
        
        console.print(f"[blue]Downloading model: {model_name}[/blue]")
        success = manager.download_model(model_name, force=force)
        
        if success:
            console.print(f"[green]Successfully downloaded {model_name}[/green]")
        else:
            console.print(f"[red]Failed to download {model_name}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error downloading model: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@models.command("status")
@click.pass_context
def model_status(ctx: click.Context) -> None:
    """Check the status of AI models."""
    from ..models.model_manager import ModelManager
    
    try:
        manager = ModelManager()
        status = manager.get_status()
        
        console.print("[bold blue]Model Status:[/bold blue]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Models Directory", str(status.get("models_dir", "Unknown")))
        table.add_row("Installed Models", str(status.get("installed_count", 0)))
        table.add_row("Total Size", status.get("total_size", "Unknown"))
        table.add_row("Default Model", status.get("default_model", "None"))
        
        console.print(table)
        
        if status.get("installed_models"):
            console.print("\n[bold blue]Installed Models:[/bold blue]")
            for model in status["installed_models"]:
                console.print(f"  • {model}")
        
    except Exception as e:
        console.print(f"[red]Error checking model status: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@main.command()
@click.option("--show", is_flag=True, help="Show current configuration")
@click.option("--init", is_flag=True, help="Initialize default configuration")
@click.option("--set", "set_option", type=str, help="Set configuration option (key=value)")
@click.pass_context
def config(ctx: click.Context, show: bool, init: bool, set_option: Optional[str]) -> None:
    """Manage configuration settings."""
    from ..utils.config import ConfigManager
    
    try:
        config_manager = ConfigManager()
        
        if init:
            config_manager.create_default_config()
            console.print("[green]Default configuration created.[/green]")
            return
            
        if set_option:
            if "=" not in set_option:
                console.print("[red]Invalid format. Use key=value[/red]")
                return
            key, value = set_option.split("=", 1)
            config_manager.set_option(key.strip(), value.strip())
            console.print(f"[green]Set {key} = {value}[/green]")
            return
            
        if show:
            config_data = config_manager.get_config()
            console.print("[bold blue]Current Configuration:[/bold blue]")
            
            def print_dict(d, indent=0):
                for key, value in d.items():
                    if isinstance(value, dict):
                        console.print("  " * indent + f"[cyan]{key}:[/cyan]")
                        print_dict(value, indent + 1)
                    else:
                        console.print("  " * indent + f"[cyan]{key}:[/cyan] {value}")
            
            print_dict(config_data)
        else:
            console.print("Use --show to display configuration, --init to create default config")
            
    except Exception as e:
        console.print(f"[red]Error managing configuration: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main() 