"""
Query generation CLI module for LawFirm-RAG.

Handles the 'query' command functionality for generating legal database search queries.
"""

import json
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core.document_processor import DocumentProcessor
from ..core.ai_engine import AIEngine
from ..core.query_generator import QueryGenerator
from ..utils.config import ConfigManager

console = Console()


def generate_queries(
    files: tuple,
    database: str = "westlaw",
    all_databases: bool = False,
    output: Optional[str] = None,
    format: str = "text",
    verbose: bool = False,
    config: Optional[str] = None
) -> None:
    """Generate search queries for legal databases.
    
    Args:
        files: Tuple of file paths to process
        database: Target database name
        all_databases: Generate queries for all supported databases
        output: Output file path
        format: Output format (json, yaml, text)
        verbose: Enable verbose output
        config: Path to configuration file
    """
    # Load configuration
    config_manager = ConfigManager(config_path=config)
    config_data = config_manager.get_config()
    
    # Initialize components
    doc_processor = DocumentProcessor()
    ai_engine = None
    
    # Try to load AI model using new backend system
    try:
        from ..core.ai_engine import create_ai_engine_from_config
        
        ai_engine = create_ai_engine_from_config(config_data)
        
        if not ai_engine.load_model():
            console.print("[yellow]Warning: Could not load AI model with new backend system. Using fallback query generation.[/yellow]")
            ai_engine = None
        else:
            console.print("[green]AI model loaded successfully with new backend system[/green]")
            
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to initialize AI engine: {e}. Using fallback query generation.[/yellow]")
        ai_engine = None
    
    # Initialize query generator
    query_gen = QueryGenerator(ai_engine)
    
    # Collect all files to process
    file_paths = []
    for file_path in files:
        path = Path(file_path)
        if path.is_file():
            file_paths.append(path)
        elif path.is_dir():
            console.print(f"[yellow]Skipping directory {path} (directories not supported for query generation)[/yellow]")
    
    if not file_paths:
        console.print("[red]No files to process.[/red]")
        return
    
    console.print(f"[blue]Generating queries for {len(file_paths)} files...[/blue]")
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        for file_path in file_paths:
            task = progress.add_task(f"Processing {file_path.name}...", total=None)
            
            try:
                # Extract text
                text = doc_processor.extract_text(file_path)
                
                if verbose:
                    console.print(f"[green]Extracted {len(text)} characters from {file_path.name}[/green]")
                
                # Generate queries
                if all_databases:
                    query_results = query_gen.generate_multiple_queries(text)
                else:
                    single_result = query_gen.generate_query(text, database)
                    query_results = {database: single_result}
                
                result = {
                    "file": str(file_path),
                    "text_length": len(text),
                    "queries": query_results
                }
                
                results.append(result)
                progress.update(task, completed=True)
                
            except Exception as e:
                console.print(f"[red]Error processing {file_path}: {e}[/red]")
                progress.update(task, completed=True)
                continue
    
    # Output results
    if output:
        _save_query_results(results, output, format)
        console.print(f"[green]Results saved to {output}[/green]")
    else:
        _display_query_results(results, format)


def _save_query_results(results: List[Dict[str, Any]], output_path: str, format: str) -> None:
    """Save query results to file.
    
    Args:
        results: Query generation results
        output_path: Output file path
        format: Output format
    """
    output_file = Path(output_path)
    
    if format == "json":
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
    elif format == "yaml":
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
            
    elif format == "text":
        with open(output_file, "w", encoding="utf-8") as f:
            for result in results:
                f.write(f"File: {result['file']}\n")
                f.write(f"Text Length: {result['text_length']} characters\n\n")
                
                for db_name, query_data in result['queries'].items():
                    f.write(f"Database: {db_name.upper()}\n")
                    
                    if "error" in query_data:
                        f.write(f"Error: {query_data['error']}\n")
                    else:
                        f.write(f"Query: {query_data['query']}\n")
                        f.write(f"Confidence: {query_data.get('confidence', 0):.2f}\n")
                        f.write(f"Method: {query_data.get('metadata', {}).get('method', 'unknown')}\n")
                        
                        if query_data.get('suggestions'):
                            f.write("Suggestions:\n")
                            for suggestion in query_data['suggestions']:
                                f.write(f"  • {suggestion}\n")
                    
                    f.write("\n")
                
                f.write("-" * 80 + "\n\n")


def _display_query_results(results: List[Dict[str, Any]], format: str) -> None:
    """Display query results to console.
    
    Args:
        results: Query generation results
        format: Output format
    """
    if format == "json":
        console.print_json(json.dumps(results, indent=2))
        
    elif format == "yaml":
        console.print(yaml.dump(results, default_flow_style=False))
        
    else:  # text format
        for i, result in enumerate(results):
            if i > 0:
                console.print()
                
            console.print(f"[bold blue]File:[/bold blue] {result['file']}")
            console.print(f"[bold blue]Text Length:[/bold blue] {result['text_length']} characters")
            console.print()
            
            for db_name, query_data in result['queries'].items():
                console.print(f"[bold cyan]Database: {db_name.upper()}[/bold cyan]")
                
                if "error" in query_data:
                    console.print(f"[red]Error: {query_data['error']}[/red]")
                else:
                    # Create table for query information
                    table = Table(show_header=False, box=None, padding=(0, 1))
                    table.add_column("Property", style="bold")
                    table.add_column("Value")
                    
                    table.add_row("Query:", f"[green]{query_data['query']}[/green]")
                    table.add_row("Confidence:", f"{query_data.get('confidence', 0):.2f}")
                    table.add_row("Method:", query_data.get('metadata', {}).get('method', 'unknown'))
                    
                    console.print(table)
                    
                    # Display suggestions if available
                    if query_data.get('suggestions'):
                        console.print("\n[bold yellow]Suggestions:[/bold yellow]")
                        for suggestion in query_data['suggestions']:
                            console.print(f"  • {suggestion}")
                
                console.print()
            
            if i < len(results) - 1:
                console.print("-" * 80) 