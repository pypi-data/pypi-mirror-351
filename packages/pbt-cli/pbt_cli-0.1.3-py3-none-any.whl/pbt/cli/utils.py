"""Shared utilities for PBT CLI commands"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

def load_prompt_file(file_path: Path) -> Dict[str, Any]:
    """Load a prompt YAML file"""
    if not file_path.exists():
        console.print(f"[red]❌ File not found: {file_path}[/red]")
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def save_prompt_file(file_path: Path, data: Dict[str, Any]) -> None:
    """Save data to a prompt YAML file"""
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def display_test_results(results: Dict[str, Any], save_results: bool = True, test_name: str = "test") -> None:
    """Display test results in a formatted table"""
    if 'test_results' not in results:
        console.print("[yellow]⚠️ No test results found[/yellow]")
        return
    
    # Create results table
    table = Table(title="Test Results", show_header=True, header_style="bold magenta")
    table.add_column("Test Name", style="cyan", no_wrap=True)
    table.add_column("Status", style="green", no_wrap=True)
    table.add_column("Score", justify="right")
    table.add_column("Execution Time", justify="right")
    table.add_column("Details")
    
    total_score = 0
    test_count = 0
    
    for test in results['test_results']:
        status = "✅ Pass" if test.get('passed', False) else "❌ Fail"
        score = test.get('score', 0)
        total_score += score
        test_count += 1
        
        details = []
        if 'error' in test:
            details.append(f"[red]Error: {test['error']}[/red]")
        if 'output' in test:
            output_preview = str(test['output'])[:50] + "..." if len(str(test['output'])) > 50 else str(test['output'])
            details.append(f"Output: {output_preview}")
        
        table.add_row(
            test.get('name', 'Unnamed'),
            status,
            f"{score:.1f}/10",
            f"{test.get('execution_time', 0):.2f}s",
            "\n".join(details) if details else "N/A"
        )
    
    console.print(table)
    
    # Summary
    avg_score = total_score / test_count if test_count > 0 else 0
    console.print(f"\n[bold]📊 Summary:[/bold]")
    console.print(f"  • Tests run: {test_count}")
    console.print(f"  • Average score: [{'green' if avg_score >= 7 else 'yellow' if avg_score >= 5 else 'red'}]{avg_score:.1f}/10[/]")
    console.print(f"  • Total time: {results.get('total_time', 0):.2f}s")
    
    # Save results if requested
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("evaluations")
        results_dir.mkdir(exist_ok=True)
        results_file = results_dir / f"{test_name}_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"\n[green]✅ Results saved to: {results_file}[/green]")

def display_performance_results(perf_results: Dict[str, Any]) -> None:
    """Display performance comparison results"""
    if not perf_results:
        return
    
    # Create performance table
    table = Table(title="Performance Comparison", show_header=True, header_style="bold cyan")
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Avg Response Time", justify="right")
    table.add_column("Tokens/sec", justify="right")
    table.add_column("Success Rate", justify="right")
    table.add_column("Avg Score", justify="right")
    
    for model, stats in perf_results.items():
        table.add_row(
            model,
            f"{stats.get('avg_response_time', 0):.2f}s",
            f"{stats.get('tokens_per_second', 0):.1f}",
            f"{stats.get('success_rate', 0)*100:.1f}%",
            f"{stats.get('avg_score', 0):.1f}/10"
        )
    
    console.print(table)

def parse_variables(variables_str: Optional[str]) -> Dict[str, Any]:
    """Parse variables from command line string"""
    if not variables_str:
        return {}
    
    try:
        # Try parsing as JSON first
        return json.loads(variables_str)
    except json.JSONDecodeError:
        # Fall back to key=value parsing
        vars_dict = {}
        for pair in variables_str.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                vars_dict[key.strip()] = value.strip()
        return vars_dict

def format_prompt_display(prompt_data: Dict[str, Any]) -> None:
    """Display a prompt in a formatted way"""
    console.print(Panel(
        Syntax(yaml.dump(prompt_data, default_flow_style=False), "yaml", theme="monokai"),
        title=f"[bold cyan]{prompt_data.get('name', 'Unnamed Prompt')}[/bold cyan]",
        border_style="cyan"
    ))

def ensure_project_initialized() -> bool:
    """Check if we're in a PBT project directory"""
    if not Path("pbt.yaml").exists():
        console.print("[yellow]⚠️ No pbt.yaml found. Run 'pbt init' first.[/yellow]")
        return False
    return True

def get_project_config() -> Dict[str, Any]:
    """Load project configuration"""
    config_path = Path("pbt.yaml")
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}

def save_project_config(config: Dict[str, Any]) -> None:
    """Save project configuration"""
    with open("pbt.yaml", 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)