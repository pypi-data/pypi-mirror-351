"""Core PBT CLI commands"""

import typer
from pathlib import Path
from typing import Optional, List
import yaml
import json
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from pbt.core.project import PBTProject
from pbt.core.prompt_generator import PromptGenerator
from pbt.core.prompt_renderer import PromptRenderer
from pbt.cli.utils import (
    console, 
    load_prompt_file, 
    save_prompt_file,
    format_prompt_display,
    parse_variables
)

def init_command(
    project_name: str = typer.Argument("my-prompts", help="Name of the project"),
    template: str = typer.Option("default", "--template", "-t", help="Project template to use")
):
    """🎯 Initialize a new PBT project"""
    console.print(f"[bold blue]🎯 Initializing PBT project: {project_name}[/bold blue]")
    
    # Create project directory
    project_path = Path(project_name)
    if project_path.exists():
        console.print(f"[red]❌ Directory '{project_name}' already exists[/red]")
        raise typer.Exit(1)
    
    project_path.mkdir(parents=True)
    
    # Create directory structure
    dirs = ["prompts", "tests", "chains", "evaluations", "deployments", "docs"]
    for dir_name in dirs:
        (project_path / dir_name).mkdir()
    
    # Create pbt.yaml
    config = {
        "name": project_name,
        "version": "0.1.0",
        "description": f"{project_name} - PBT project for prompt engineering",
        "models": {
            "default": "gpt-3.5-turbo",
            "available": ["gpt-3.5-turbo", "gpt-4", "claude-3-opus", "claude-3-sonnet"]
        },
        "settings": {
            "test_timeout": 30,
            "max_retries": 3,
            "temperature": 0.7
        }
    }
    
    with open(project_path / "pbt.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    # Create .env.example
    env_content = """# PBT Environment Variables
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
"""
    
    with open(project_path / ".env.example", "w") as f:
        f.write(env_content)
    
    # Create .gitignore
    gitignore_content = """.env
*.pyc
__pycache__/
evaluations/
deployments/local/
.pbt_cache/
"""
    
    with open(project_path / ".gitignore", "w") as f:
        f.write(gitignore_content)
    
    # Create README
    readme_content = f"""# {project_name}

A PBT (Prompt Build Tool) project for infrastructure-grade prompt engineering.

## Setup

1. Copy `.env.example` to `.env` and add your API keys
2. Generate your first prompt: `pbt generate --goal "Your goal here"`
3. Test it: `pbt test prompts/*.yaml`

## Project Structure

- `prompts/` - Your prompt files
- `tests/` - Test cases for prompts
- `chains/` - Multi-agent workflows
- `evaluations/` - Test results
- `deployments/` - Deployment configurations
"""
    
    with open(project_path / "README.md", "w") as f:
        f.write(readme_content)
    
    console.print(f"[green]✅ Project initialized successfully![/green]")
    console.print(f"\n[bold]Next steps:[/bold]")
    console.print(f"1. [cyan]cd {project_name}[/cyan]")
    console.print(f"2. [cyan]cp .env.example .env[/cyan] and add your API keys")
    console.print(f"3. [cyan]pbt generate --goal \"Your prompt goal\"[/cyan]")

def generate_command(
    goal: str = typer.Option(..., "--goal", "-g", help="The goal or purpose of the prompt"),
    variables: Optional[List[str]] = typer.Option(None, "--var", "-v", help="Variables the prompt should accept"),
    examples: Optional[List[str]] = typer.Option(None, "--example", "-e", help="Example inputs/outputs"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    model: str = typer.Option("claude-3-opus", "--model", "-m", help="Model to optimize for"),
    test_count: int = typer.Option(5, "--tests", "-t", help="Number of test cases to generate")
):
    """🤖 Generate a new prompt using AI"""
    console.print(f"[bold blue]🤖 Generating prompt for goal: {goal}[/bold blue]")
    
    # Initialize project
    project = PBTProject()
    generator = PromptGenerator(project)
    
    # Process examples
    processed_examples = []
    if examples:
        for example in examples:
            if ":" in example:
                input_part, output_part = example.split(":", 1)
                processed_examples.append({
                    "input": input_part.strip(),
                    "output": output_part.strip()
                })
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Generating prompt...", total=1)
        
        # Generate the prompt
        result = generator.generate_prompt(
            goal=goal,
            variables=variables or [],
            examples=processed_examples if processed_examples else None,
            constraints=None
        )
        
        progress.update(task, completed=1)
    
    if result['success']:
        # Determine output filename
        if output:
            prompt_path = output
        else:
            # Generate filename from goal
            name_parts = goal.lower().split()[:3]
            filename = "-".join(name_parts) + ".prompt.yaml"
            prompt_path = Path("prompts") / filename
            prompt_path.parent.mkdir(exist_ok=True)
        
        # Save the prompt
        prompt_data = result['prompt']
        prompt_data['model'] = model
        
        save_prompt_file(prompt_path, prompt_data)
        console.print(f"[green]✅ Prompt saved to: {prompt_path}[/green]")
        
        # Display the generated prompt
        format_prompt_display(prompt_data)
        
        # Generate test cases if requested
        if test_count > 0 and result.get('tests'):
            test_path = Path("tests") / f"{prompt_path.stem}.test.yaml"
            test_path.parent.mkdir(exist_ok=True)
            
            test_data = {
                'tests': result['tests'][:test_count]
            }
            
            save_prompt_file(test_path, test_data)
            console.print(f"[green]✅ Test cases saved to: {test_path}[/green]")
        
        # Next steps
        console.print("\n[bold yellow]🚀 Next steps:[/bold yellow]")
        console.print(f"1. Review and edit: [cyan]{prompt_path}[/cyan]")
        console.print(f"2. Test it: [cyan]pbt test {prompt_path}[/cyan]")
        console.print(f"3. Compare models: [cyan]pbt compare {prompt_path}[/cyan]")
        console.print(f"4. Optimize: [cyan]pbt optimize {prompt_path}[/cyan]")
    else:
        console.print(f"[red]❌ Failed to generate prompt: {result.get('error', 'Unknown error')}[/red]")
        raise typer.Exit(1)

def draft_command(
    text: str = typer.Argument(..., help="Plain text to convert into a structured prompt"),
    goal: Optional[str] = typer.Option(None, "--goal", "-g", help="Goal or purpose for the prompt"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    variables: Optional[List[str]] = typer.Option(None, "--var", "-v", help="Variables to include"),
    model: str = typer.Option("claude-3-opus", "--model", "-m", help="Default model"),
    generate_tests: bool = typer.Option(True, "--tests/--no-tests", help="Generate test cases"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode")
):
    """✏️ Draft a structured prompt from plain text"""
    console.print(f"[bold blue]✏️ Drafting structured prompt from text[/bold blue]")
    console.print(f"[cyan]📝 Text: {text[:100]}{'...' if len(text) > 100 else ''}[/cyan]")
    
    try:
        project = PBTProject()
        enhanced_goal = goal if goal else f"Create a prompt that: {text}"
        
        if variables:
            enhanced_goal += f"\n\nThe prompt should accept these variables: {', '.join(variables)}"
        
        generator = PromptGenerator(project)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Analyzing text and generating prompt structure...", total=1)
            
            result = generator.generate_prompt(
                goal=enhanced_goal,
                variables=variables if variables else [],
                examples=None,
                constraints=[f"Base the prompt on this text pattern: {text}"]
            )
            
            progress.update(task, completed=1)
        
        if result['success']:
            if output:
                prompt_path = output
            else:
                name_parts = text.lower().split()[:3]
                filename = "-".join(name_parts) + ".prompt.yaml"
                prompt_path = Path(filename)
            
            prompt_data = result['prompt']
            
            if 'metadata' not in prompt_data:
                prompt_data['metadata'] = {}
            prompt_data['metadata']['original_text'] = text
            prompt_data['metadata']['generated_from'] = 'draft'
            
            if model:
                prompt_data['model'] = model
            
            if interactive:
                console.print("\n[yellow]🔍 Generated Prompt Preview:[/yellow]")
                console.print(Panel(prompt_data['template'], title="Prompt Template"))
                
                if typer.confirm("\n✏️  Would you like to refine this prompt?"):
                    new_template = typer.prompt("Enter refined prompt", default=prompt_data['template'])
                    prompt_data['template'] = new_template
            
            save_prompt_file(prompt_path, prompt_data)
            console.print(f"\n[green]✅ Prompt saved to: {prompt_path}[/green]")
            
            format_prompt_display(prompt_data)
            
            if generate_tests:
                test_path = Path(f"tests/{prompt_path.stem}.test.yaml")
                if result.get('tests'):
                    test_path.parent.mkdir(exist_ok=True)
                    save_prompt_file(test_path, {'tests': result['tests']})
                    console.print(f"\n[green]✅ Tests saved to: {test_path}[/green]")
            
            console.print("\n[bold yellow]🚀 Next steps:[/bold yellow]")
            console.print(f"1. Test your prompt: [cyan]pbt test {prompt_path}[/cyan]")
            console.print(f"2. Compare models: [cyan]pbt compare {prompt_path}[/cyan]")
            console.print(f"3. Optimize: [cyan]pbt optimize {prompt_path}[/cyan]")
            console.print(f"4. Interactive UI: [cyan]pbt web[/cyan]")
            
        else:
            console.print(f"[red]❌ Failed to generate prompt: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

def render_command(
    prompt_file: Path = typer.Argument(..., help="Path to the prompt file"),
    variables: Optional[str] = typer.Option(None, "--vars", "-v", help="Variables as JSON or key=value pairs"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use for rendering"),
    compare: bool = typer.Option(False, "--compare", "-c", help="Compare across multiple models"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save rendered output to file")
):
    """🖨️ Render a prompt with variables"""
    console.print(f"[bold blue]🖨️ Rendering prompt: {prompt_file}[/bold blue]")
    
    # Load prompt
    prompt_data = load_prompt_file(prompt_file)
    
    # Parse variables
    vars_dict = parse_variables(variables)
    
    # Initialize renderer
    project = PBTProject()
    renderer = PromptRenderer(project)
    
    if compare:
        # Compare across models
        models = prompt_data.get('models', ['gpt-3.5-turbo', 'gpt-4', 'claude-3-opus'])
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Comparing across {len(models)} models...", total=len(models))
            
            for model_name in models:
                result = renderer.render(prompt_data, vars_dict, model=model_name)
                results[model_name] = result
                progress.advance(task)
        
        # Display comparison
        for model_name, result in results.items():
            console.print(f"\n[bold cyan]Model: {model_name}[/bold cyan]")
            if result['success']:
                console.print(Panel(
                    result['output'],
                    title=f"Output from {model_name}",
                    border_style="cyan"
                ))
            else:
                console.print(f"[red]Error: {result['error']}[/red]")
    else:
        # Single model rendering
        result = renderer.render(prompt_data, vars_dict, model=model)
        
        if result['success']:
            console.print(Panel(
                result['output'],
                title="Rendered Output",
                border_style="green"
            ))
            
            if output:
                with open(output, 'w') as f:
                    f.write(result['output'])
                console.print(f"\n[green]✅ Output saved to: {output}[/green]")
        else:
            console.print(f"[red]❌ Rendering failed: {result['error']}[/red]")
            raise typer.Exit(1)