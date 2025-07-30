"""
Document analysis CLI module for LawFirm-RAG.

Handles the 'analyze' command functionality for processing and analyzing documents.
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
from ..utils.config import ConfigManager

console = Console()


def analyze_documents(
    files: tuple,
    output: Optional[str] = None,
    format: str = "text",
    analysis_type: str = "summary",
    recursive: bool = False,
    verbose: bool = False,
    config: Optional[str] = None
) -> None:
    """Analyze documents and generate insights.
    
    Args:
        files: Tuple of file paths to analyze
        output: Output file path
        format: Output format (json, yaml, text)
        analysis_type: Type of analysis (summary, key_points, legal_issues)
        recursive: Process directories recursively
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
            console.print("[yellow]Warning: Could not load AI model with new backend system. Using fallback analysis.[/yellow]")
            ai_engine = None
        else:
            console.print("[green]AI model loaded successfully with new backend system[/green]")
            
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to initialize AI engine: {e}. Using fallback analysis.[/yellow]")
        ai_engine = None
    
    # Collect all files to process
    file_paths = []
    for file_path in files:
        path = Path(file_path)
        if path.is_file():
            file_paths.append(path)
        elif path.is_dir() and recursive:
            # Find supported document files
            for ext in [".pdf", ".docx", ".txt"]:
                file_paths.extend(path.rglob(f"*{ext}"))
        elif path.is_dir():
            console.print(f"[yellow]Skipping directory {path} (use --recursive to process)[/yellow]")
    
    if not file_paths:
        console.print("[red]No files to process.[/red]")
        return
    
    console.print(f"[blue]Processing {len(file_paths)} files...[/blue]")
    
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
                
                # Perform analysis
                analysis_result = None
                if ai_engine and ai_engine.is_loaded:
                    try:
                        analysis_result = ai_engine.analyze_document(text, analysis_type)
                    except Exception as e:
                        console.print(f"[yellow]AI analysis failed for {file_path.name}: {e}[/yellow]")
                
                # Fallback analysis if AI not available
                if not analysis_result:
                    analysis_result = _fallback_analysis(text, analysis_type)
                
                result = {
                    "file": str(file_path),
                    "analysis_type": analysis_type,
                    "text_length": len(text),
                    "analysis": analysis_result,
                    "method": "ai" if ai_engine and ai_engine.is_loaded else "fallback"
                }
                
                results.append(result)
                progress.update(task, completed=True)
                
            except Exception as e:
                console.print(f"[red]Error processing {file_path}: {e}[/red]")
                progress.update(task, completed=True)
                continue
    
    # Output results
    if output:
        _save_results(results, output, format)
        console.print(f"[green]Results saved to {output}[/green]")
    else:
        _display_results(results, format)


def _fallback_analysis(text: str, analysis_type: str) -> str:
    """Provide basic analysis when AI model is not available.
    
    Args:
        text: Document text
        analysis_type: Type of analysis
        
    Returns:
        Basic analysis result
    """
    words = text.split()
    sentences = text.split('.')
    
    if analysis_type == "summary":
        # Simple extractive summary - first few sentences
        summary_sentences = sentences[:3]
        return ". ".join(s.strip() for s in summary_sentences if s.strip()) + "."
        
    elif analysis_type == "key_points":
        # Look for common legal terms and patterns
        legal_terms = [
            "contract", "agreement", "liability", "negligence", "breach",
            "damages", "plaintiff", "defendant", "court", "statute"
        ]
        
        found_terms = []
        text_lower = text.lower()
        for term in legal_terms:
            if term in text_lower:
                found_terms.append(term.title())
        
        if found_terms:
            return "• " + "\n• ".join(f"Document mentions: {term}" for term in found_terms[:5])
        else:
            return "• Document contains legal content\n• Length: {} words\n• {} sentences".format(
                len(words), len(sentences)
            )
            
    elif analysis_type == "legal_issues":
        # Basic pattern matching for legal issues
        issues = []
        text_lower = text.lower()
        
        if "contract" in text_lower or "agreement" in text_lower:
            issues.append("Contract Law")
        if "negligence" in text_lower or "liability" in text_lower:
            issues.append("Tort Law")
        if "court" in text_lower or "litigation" in text_lower:
            issues.append("Civil Procedure")
        if "statute" in text_lower or "regulation" in text_lower:
            issues.append("Regulatory Compliance")
            
        if issues:
            return "Potential legal areas:\n• " + "\n• ".join(issues)
        else:
            return "Legal document requiring professional analysis"
    
    return f"Basic analysis: {len(words)} words, {len(sentences)} sentences"


def _save_results(results: List[Dict[str, Any]], output_path: str, format: str) -> None:
    """Save analysis results to file.
    
    Args:
        results: Analysis results
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
                f.write(f"Analysis Type: {result['analysis_type']}\n")
                f.write(f"Method: {result['method']}\n")
                f.write(f"Text Length: {result['text_length']} characters\n")
                f.write(f"\nAnalysis:\n{result['analysis']}\n")
                f.write("-" * 80 + "\n\n")


def _display_results(results: List[Dict[str, Any]], format: str) -> None:
    """Display analysis results to console.
    
    Args:
        results: Analysis results
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
            console.print(f"[bold blue]Analysis Type:[/bold blue] {result['analysis_type']}")
            console.print(f"[bold blue]Method:[/bold blue] {result['method']}")
            console.print(f"[bold blue]Text Length:[/bold blue] {result['text_length']} characters")
            console.print(f"\n[bold blue]Analysis:[/bold blue]")
            console.print(result['analysis'])
            
            if i < len(results) - 1:
                console.print("\n" + "-" * 80) 