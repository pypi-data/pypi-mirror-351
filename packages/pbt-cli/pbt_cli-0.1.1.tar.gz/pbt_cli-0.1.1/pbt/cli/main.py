#!/usr/bin/env python3
"""
PBT CLI - Main entry point (Refactored)
"""

# Load .env files before any other imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import typer
from typing import Optional
from pathlib import Path

from pbt.__version__ import __version__
from pbt.cli.utils import console

# Import commands from modules
from pbt.cli.commands.core import (
    init_command,
    generate_command,
    draft_command,
    render_command
)
from pbt.cli.commands.testing import (
    test_command,
    testcomp_command,
    compare_command,
    validate_command
)
from pbt.cli.commands.optimization import (
    optimize_command,
    eval_command,
    chunk_command
)

# Create the main app
app = typer.Typer(
    name="pbt",
    help="🚀 Prompt Build Tool - Infrastructure-grade prompt engineering for AI teams",
    add_completion=False,
    rich_markup_mode="rich"
)

def version_callback(value: bool):
    """Display version information"""
    if value:
        console.print(f"[bold blue]PBT (Prompt Build Tool)[/bold blue] version [green]{__version__}[/green]")
        console.print("\n[dim]To get started:[/dim]")
        console.print("1. [cyan]pbt init[/cyan] - Initialize new project")
        console.print("2. Add [yellow]ANTHROPIC_API_KEY[/yellow] to .env file")
        console.print("3. [cyan]pbt generate --goal 'Your prompt goal'[/cyan]")
        console.print("\n[dim]Need API keys? See: docs/API_KEYS.md[/dim]")
        raise typer.Exit()

def show_welcome_screen():
    """Display welcome screen with introduction"""
    console.print()
    console.print("[bold blue]🚀 Welcome to PBT (Prompt Build Tool)[/bold blue]")
    console.print(f"[dim]Version {__version__}[/dim]")
    console.print()
    
    console.print("[bold]Infrastructure-grade prompt engineering for AI teams[/bold]")
    console.print("PBT is like [yellow]dbt + Terraform[/yellow] for LLM prompts")
    console.print()
    
    # Key features
    console.print("[bold cyan]✨ Key Features:[/bold cyan]")
    features = [
        "🎯 AI-powered prompt generation",
        "🧪 Cross-model testing & comparison", 
        "🌐 Interactive web UI",
        "📊 Automatic scoring",
        "💰 Cost optimization",
        "🔗 Multi-agent chains"
    ]
    
    for feature in features:
        console.print(f"  {feature}")
    console.print()
    
    # Quick start
    console.print("[bold green]🚀 Quick Start:[/bold green]")
    console.print("1. [cyan]pbt init my-prompts[/cyan]")
    console.print("2. [cyan]cd my-prompts[/cyan]")
    console.print("3. [cyan]pbt generate --goal \"Your goal\"[/cyan]")
    console.print()
    
    console.print("[dim]Run [cyan]pbt --help[/cyan] for all commands[/dim]")

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v",
        callback=version_callback,
        help="Show version and exit"
    )
):
    """PBT CLI main entry point"""
    if ctx.invoked_subcommand is None:
        show_welcome_screen()

# Register core commands
app.command(name="init")(init_command)
app.command(name="generate")(generate_command)
app.command(name="draft")(draft_command)
app.command(name="d")(lambda *args, **kwargs: draft_command(*args, **kwargs))  # Shorthand
app.command(name="render")(render_command)

# Register testing commands
app.command(name="test")(test_command)
app.command(name="testcomp")(testcomp_command)
app.command(name="compare")(compare_command)
app.command(name="validate")(validate_command)

# Register optimization commands
app.command(name="optimize")(optimize_command)
app.command(name="eval")(eval_command)
app.command(name="chunk")(chunk_command)

# Web UI command
@app.command()
def web(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8080, "--port", "-p", help="Port to bind to"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open browser automatically")
):
    """🌐 Launch interactive web UI for visual prompt comparison"""
    console.print(f"[bold blue]🌐 Starting PBT Web UI...[/bold blue]")
    
    try:
        import webbrowser
        import uvicorn
        from pbt.web.app import app as web_app
        
        url = f"http://{host}:{port}"
        console.print(f"[green]✅ Web UI starting at: {url}[/green]")
        
        if open_browser:
            import threading
            import time
            def open_browser_delayed():
                time.sleep(1.5)
                webbrowser.open(url)
            
            threading.Thread(target=open_browser_delayed).start()
        
        console.print("[dim]Press Ctrl+C to stop the server[/dim]")
        uvicorn.run(web_app, host=host, port=port, log_level="error")
        
    except ImportError as e:
        console.print(f"[red]❌ Missing dependency: {e}[/red]")
        console.print("[yellow]Install with: pip install 'pbt-cli[web]'[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error starting web server: {e}[/red]")
        raise typer.Exit(1)

# Additional utility commands
@app.command()
def convert(
    input_file: str = typer.Argument(..., help="Python file or directory to convert"),
    output_dir: Path = typer.Option(Path("prompts"), "--output", "-o", help="Output directory"),
    batch: bool = typer.Option(False, "--batch", "-b", help="Batch convert directory")
):
    """🔄 Convert Python agents to PBT format"""
    console.print(f"[bold blue]🔄 Converting: {input_file}[/bold blue]")
    
    from pbt.core.converter import Converter
    from pbt.core.project import PBTProject
    
    project = PBTProject()
    converter = Converter(project)
    
    try:
        if batch:
            results = converter.convert_directory(Path(input_file), output_dir)
            console.print(f"[green]✅ Converted {results['converted']} files[/green]")
            if results['errors']:
                console.print(f"[yellow]⚠️ {results['errors']} errors[/yellow]")
        else:
            result = converter.convert_file(Path(input_file), output_dir)
            if result['success']:
                console.print(f"[green]✅ Converted to: {result['output_file']}[/green]")
            else:
                console.print(f"[red]❌ Conversion failed: {result['error']}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()