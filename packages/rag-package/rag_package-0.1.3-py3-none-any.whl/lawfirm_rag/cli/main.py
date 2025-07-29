"""
Main CLI entry point for LawFirm-RAG package.

Provides command-line interface for document analysis, query generation,
and server management.
"""

import sys
import click
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .. import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="rag")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.pass_context
def main(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """
    RAG: AI-Powered Legal Document Analysis Package
    
    A modern Python package for legal document analysis, query generation,
    and AI-powered legal research assistance.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config
    
    if verbose:
        console.print(f"[green]RAG v{__version__}[/green]")
        if config:
            console.print(f"[blue]Using config: {config}[/blue]")


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
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool, 
          api_key: Optional[str], cors: bool) -> None:
    """Start the RAG web server."""
    from .server import start_server
    
    try:
        start_server(
            host=host,
            port=port,
            reload=reload,
            api_key=api_key,
            cors=cors,
            verbose=ctx.obj.get("verbose", False),
            config=ctx.obj.get("config")
        )
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
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