#!/usr/bin/env python3
"""
Environment Manager for LawFirm-RAG Package.

Handles automatic virtual environment creation, dependency installation,
and environment activation for optimal AI/ML package isolation.
"""

import os
import sys
import subprocess
import venv
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import tempfile
import json

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import print as rprint

console = Console()

# Environment configuration
RAG_ENV_NAME = ".rag-env"
RAG_REQUIREMENTS = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0", 
    "python-multipart>=0.0.6",
    "pydantic>=2.0.0",
    "click>=8.0.0",
    "requests>=2.31.0",
    "python-docx>=0.8.11",
    "PyPDF2>=3.0.0",
    "psutil>=5.9.0",
    "rich>=13.0.0",
    "Jinja2>=3.1.0",
    "PyYAML>=6.0",
    "python-dotenv>=1.0.0",
    # Document processing - enhanced
    "pdfplumber==0.9.0",
    "PyMuPDF==1.23.8",
    # Vector database and embeddings - WORKING VERSIONS
    "chromadb==0.4.15",
    "numpy==1.24.3",
    "sentence-transformers==4.1.0",  # Latest stable version - tested working
    "torch==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu",  # CPU-optimized with index URL
    # AI/ML backends
    "ollama==0.1.9",
]


def get_python_executable() -> str:
    """Get the appropriate Python 3.11+ executable."""
    candidates = ["python3.11", "python3.12", "python3", "python"]
    
    for candidate in candidates:
        try:
            result = subprocess.run(
                [candidate, "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            version_str = result.stdout.strip()
            # Extract version number (e.g., "Python 3.11.0" -> "3.11.0")
            version = version_str.split()[1]
            major, minor = map(int, version.split('.')[:2])
            
            if major == 3 and minor >= 11:
                return candidate
                
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError, IndexError):
            continue
    
    raise RuntimeError(
        "Python 3.11+ is required but not found. Please install Python 3.11 or newer.\n"
        "Visit: https://www.python.org/downloads/"
    )


def find_rag_environment() -> Optional[Path]:
    """Find any existing RAG environment, checking multiple possible locations."""
    candidates = []
    
    if sys.platform == "win32":
        # Check all possible Windows locations
        candidates = [
            Path("C:/rag"),           # Force short path
            Path("C:/rag-env"),       # Default short path  
            Path.home() / "rag-env",  # Home directory
            Path.home() / RAG_ENV_NAME,  # Home with dot prefix
        ]
    else:
        # Unix systems
        candidates = [
            Path.home() / RAG_ENV_NAME,
            Path.home() / "rag-env",
        ]
    
    # Return the first existing environment
    for candidate in candidates:
        marker_file = candidate / "rag_env_marker.txt"
        if marker_file.exists():
            return candidate
    
    return None


def get_rag_env_path() -> Path:
    """Get the path to the RAG virtual environment."""
    # First try to find existing environment
    existing = find_rag_environment()
    if existing:
        return existing
    
    # No existing environment, return default path for creation
    if sys.platform == "win32":
        # Use shorter path on Windows to avoid long path issues
        return Path("C:/rag-env")
    else:
        # Unix systems handle long paths better
        return Path.home() / RAG_ENV_NAME


def is_in_rag_env() -> bool:
    """Check if we're currently running in the RAG virtual environment."""
    # Check if VIRTUAL_ENV points to our RAG environment
    virtual_env = os.environ.get('VIRTUAL_ENV')
    if virtual_env:
        env_path = Path(virtual_env)
        return env_path.name == RAG_ENV_NAME or str(env_path).endswith(RAG_ENV_NAME)
    
    # Alternative check: look for our marker file
    rag_env_path = get_rag_env_path()
    marker_file = rag_env_path / "rag_env_marker.txt"
    return marker_file.exists() and os.environ.get('VIRTUAL_ENV') == str(rag_env_path)


def get_activation_script() -> Path:
    """Get the path to the activation script."""
    rag_env_path = get_rag_env_path()
    if sys.platform == "win32":
        return rag_env_path / "Scripts" / "activate.bat"
    else:
        return rag_env_path / "bin" / "activate"


class EnvironmentManager:
    """Manages RAG virtual environment setup and maintenance."""
    
    def __init__(self):
        self.rag_env_path = get_rag_env_path()
        self.python_executable = None
        
    def check_python_version(self) -> bool:
        """Check if Python 3.11+ is available."""
        try:
            self.python_executable = get_python_executable()
            console.print(f"[green]✅ Found Python: {self.python_executable}[/green]")
            return True
        except RuntimeError as e:
            console.print(f"[red]❌ {e}[/red]")
            return False
    
    def create_environment(self, force_short_path: bool = False) -> bool:
        """Create the RAG virtual environment."""
        try:
            # Use shortest path on Windows if requested
            if force_short_path and sys.platform == "win32":
                self.rag_env_path = Path("C:/rag")  # Even shorter!
                console.print(f"[blue]🔧 Using short path for Windows: {self.rag_env_path}[/blue]")
            
            console.print(f"[blue]📁 Creating environment at: {self.rag_env_path}[/blue]")
            
            # Ensure parent directory exists
            self.rag_env_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create virtual environment
            venv.create(
                self.rag_env_path,
                system_site_packages=False,
                clear=True,
                with_pip=True
            )
            
            # Create marker file
            marker_file = self.rag_env_path / "rag_env_marker.txt"
            marker_file.write_text(f"RAG Environment created by lawfirm-rag package\nVersion: 0.1.6\n")
            
            console.print("[green]✅ Virtual environment created successfully[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to create environment: {e}[/red]")
            
            # Suggest shorter path on Windows if creation failed
            if sys.platform == "win32" and not force_short_path:
                console.print("[yellow]💡 Try using a shorter path:[/yellow]")
                console.print("[cyan]rag setup --force[/cyan]")
            
            return False
    
    def get_pip_executable(self) -> Path:
        """Get the pip executable in the virtual environment."""
        if sys.platform == "win32":
            return self.rag_env_path / "Scripts" / "pip.exe"
        else:
            return self.rag_env_path / "bin" / "pip"
    
    def get_python_executable_in_venv(self) -> Path:
        """Get the python executable in the virtual environment."""
        if sys.platform == "win32":
            return self.rag_env_path / "Scripts" / "python.exe"
        else:
            return self.rag_env_path / "bin" / "python"

    def install_dependencies(self) -> bool:
        """Install all required dependencies in the virtual environment."""
        pip_executable = self.get_pip_executable()
        python_executable = self.get_python_executable_in_venv()
        
        if not python_executable.exists():
            console.print("[red]❌ Python not found in virtual environment[/red]")
            return False
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
                transient=False
            ) as progress:
                
                # Upgrade pip first using python -m pip (works better on Windows)
                task = progress.add_task("Upgrading pip...", total=len(RAG_REQUIREMENTS) + 2)
                
                result = subprocess.run(
                    [str(python_executable), "-m", "pip", "install", "--upgrade", "pip"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                progress.advance(task)
                
                # Install our package in editable mode if we're in development
                try:
                    setup_py = Path("setup.py")
                    pyproject_toml = Path("pyproject.toml")
                    if setup_py.exists() or pyproject_toml.exists():
                        progress.update(task, description="Installing package (editable)...")
                        subprocess.run(
                            [str(python_executable), "-m", "pip", "install", "-e", "."],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                except subprocess.CalledProcessError:
                    # Not in development environment, install from PyPI
                    progress.update(task, description="Installing lawfirm-rag package...")
                    subprocess.run(
                        [str(python_executable), "-m", "pip", "install", "lawfirm-rag"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                progress.advance(task)
                
                # Install all dependencies using python -m pip
                for req in RAG_REQUIREMENTS:
                    progress.update(task, description=f"Installing {req.split('==')[0]}...")
                    
                    result = subprocess.run(
                        [str(python_executable), "-m", "pip", "install", req],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        console.print(f"[yellow]⚠️  Warning: Failed to install {req}[/yellow]")
                        console.print(f"[dim]{result.stderr}[/dim]")
                    
                    progress.advance(task)
                
                progress.update(task, description="✅ Installation complete!")
            
            console.print("[green]🎉 All dependencies installed successfully![/green]")
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout or str(e)
            
            # Check for Windows long path issue
            if sys.platform == "win32" and ("long" in error_msg.lower() or "path" in error_msg.lower() or "errno 2" in error_msg.lower()):
                console.print("[red]❌ Windows Long Path Issue Detected![/red]")
                console.print("\n[yellow]🔧 To fix this:[/yellow]")
                console.print("[cyan]1. Run PowerShell as Administrator[/cyan]")
                console.print("[cyan]2. Run this command:[/cyan]")
                console.print("[green]   New-ItemProperty -Path \"HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem\" -Name \"LongPathsEnabled\" -Value 1 -PropertyType DWORD -Force[/green]")
                console.print("[cyan]3. Reboot your computer[/cyan]")
                console.print("[cyan]4. Try 'rag setup' again[/cyan]")
                console.print("\n[yellow]Alternative: Try 'rag setup --force' to use shorter paths[/yellow]")
                return False
            
            console.print(f"[red]❌ Failed to install dependencies: {e}[/red]")
            if error_msg:
                console.print(f"[dim]Error details: {error_msg}[/dim]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Unexpected error during installation: {e}[/red]")
            return False
    
    def verify_installation(self) -> bool:
        """Verify that all critical packages are properly installed."""
        python_executable = self.get_python_executable_in_venv()
        
        critical_packages = ["torch", "sentence-transformers", "chromadb", "fastapi"]
        
        try:
            # Get installed packages using python -m pip
            result = subprocess.run(
                [str(python_executable), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            installed_packages = {pkg["name"].lower(): pkg["version"] for pkg in json.loads(result.stdout)}
            
            table = Table(title="🔍 Installation Verification")
            table.add_column("Package", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Version", style="yellow")
            
            all_good = True
            for package in critical_packages:
                if package.lower() in installed_packages:
                    table.add_row(package, "✅ Installed", installed_packages[package.lower()])
                else:
                    table.add_row(package, "❌ Missing", "N/A")
                    all_good = False
            
            console.print(table)
            
            if all_good:
                console.print("[green]🎉 All critical packages verified![/green]")
            else:
                console.print("[red]❌ Some packages are missing[/red]")
            
            return all_good
            
        except Exception as e:
            console.print(f"[red]❌ Verification failed: {e}[/red]")
            return False
    
    def setup_complete_environment(self, force: bool = False) -> bool:
        """Complete environment setup process."""
        console.print(Panel.fit(
            "[bold blue]🚀 Setting up RAG Environment[/bold blue]\n"
            "This will create an isolated environment with all AI/ML dependencies",
            border_style="blue"
        ))
        
        # Check if environment already exists
        if self.rag_env_path.exists() and not force:
            console.print(f"[yellow]⚠️  Environment already exists at: {self.rag_env_path}[/yellow]")
            console.print("[cyan]Use --force to recreate it[/cyan]")
            return False
        
        # Step 1: Check Python version
        if not self.check_python_version():
            return False
        
        # Step 2: Create virtual environment (use shorter path on Windows if force is used)
        force_short_path = force and sys.platform == "win32"
        if not self.create_environment(force_short_path=force_short_path):
            return False
        
        # Step 3: Install dependencies
        if not self.install_dependencies():
            return False
        
        # Step 4: Verify installation
        if not self.verify_installation():
            console.print("[yellow]⚠️  Some packages failed verification but setup completed[/yellow]")
        
        # Step 5: Show activation instructions
        self.show_activation_instructions()
        
        return True
    
    def show_activation_instructions(self):
        """Show instructions for activating the environment."""
        activation_script = get_activation_script()
        
        console.print(Panel.fit(
            f"[bold green]🎉 Environment Setup Complete![/bold green]\n\n"
            f"[cyan]To activate your RAG environment:[/cyan]\n\n"
            f"[bold]Windows:[/bold]\n"
            f"[green]{self.rag_env_path / 'Scripts' / 'activate.bat'}[/green]\n\n"
            f"[bold]Mac/Linux:[/bold]\n"
            f"[green]source {self.rag_env_path / 'bin' / 'activate'}[/green]\n\n"
            f"[cyan]Or use the automatic activation:[/cyan]\n"
            f"[green]rag setup --activate[/green]\n\n"
            f"[cyan]Then start the server:[/cyan]\n"
            f"[green]rag serve[/green]",
            border_style="green"
        ))
    
    def activate_environment(self) -> bool:
        """Activate the RAG environment (for current session)."""
        if not self.rag_env_path.exists():
            console.print("[red]❌ RAG environment not found. Run 'rag setup' first.[/red]")
            return False
        
        # Set environment variables for this session
        if sys.platform == "win32":
            scripts_dir = self.rag_env_path / "Scripts"
            python_exe = scripts_dir / "python.exe"
        else:
            scripts_dir = self.rag_env_path / "bin" 
            python_exe = scripts_dir / "python"
        
        if not python_exe.exists():
            console.print("[red]❌ Python executable not found in environment[/red]")
            return False
        
        # Update PATH and VIRTUAL_ENV
        os.environ["VIRTUAL_ENV"] = str(self.rag_env_path)
        os.environ["PATH"] = f"{scripts_dir}{os.pathsep}{os.environ['PATH']}"
        
        # Remove PYTHONHOME if set
        os.environ.pop("PYTHONHOME", None)
        
        console.print(f"[green]✅ Activated RAG environment: {self.rag_env_path}[/green]")
        console.print("[cyan]You can now use 'rag serve' to start the application[/cyan]")
        
        return True
    
    def repair_environment(self) -> bool:
        """Repair an existing environment by reinstalling dependencies."""
        if not self.rag_env_path.exists():
            console.print("[red]❌ RAG environment not found. Run 'rag setup' first.[/red]")
            return False
        
        console.print(f"[blue]🔧 Repairing environment at: {self.rag_env_path}[/blue]")
        
        # Just reinstall dependencies in existing environment
        if not self.install_dependencies():
            return False
        
        # Verify the repair worked
        if not self.verify_installation():
            console.print("[yellow]⚠️  Some packages failed verification[/yellow]")
        
        console.print("[green]🔧 Environment repair completed![/green]")
        return True

    def remove_environment(self) -> bool:
        """Remove the RAG environment."""
        if not self.rag_env_path.exists():
            console.print("[yellow]Environment doesn't exist[/yellow]")
            return True
        
        try:
            shutil.rmtree(self.rag_env_path)
            console.print(f"[green]✅ Removed environment: {self.rag_env_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to remove environment: {e}[/red]")
            return False 