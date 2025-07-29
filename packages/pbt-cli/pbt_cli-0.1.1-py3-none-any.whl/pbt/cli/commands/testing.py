"""Testing-related PBT CLI commands"""

import typer
from pathlib import Path
from typing import Optional, List
import json
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from pbt.core.project import PBTProject
from pbt.core.prompt_evaluator import PromptEvaluator
from pbt.core.comprehensive_evaluator import ComprehensiveEvaluator
from pbt.cli.utils import (
    console,
    load_prompt_file,
    save_prompt_file,
    display_test_results,
    display_performance_results,
    parse_variables
)

def test_command(
    prompt_file: Path = typer.Argument(..., help="Path to the prompt file to test"),
    test_file: Optional[Path] = typer.Option(None, "--test-file", "-t", help="Path to test file"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use for testing"),
    num_tests: int = typer.Option(5, "--num-tests", "-n", help="Number of tests to run"),
    save_results: bool = typer.Option(True, "--save-results/--no-save-results", help="Save test results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """🧪 Test a prompt with automated evaluation"""
    console.print(f"[bold blue]🧪 Testing prompt: {prompt_file}[/bold blue]")
    
    # Load prompt
    prompt_data = load_prompt_file(prompt_file)
    
    # Initialize evaluator
    project = PBTProject()
    evaluator = PromptEvaluator(project)
    
    # Determine test file
    if not test_file:
        # Look for corresponding test file
        test_file_candidates = [
            Path(f"tests/{prompt_file.stem}.test.yaml"),
            Path(f"tests/{prompt_file.stem}.test.jsonl"),
            prompt_file.with_suffix('.test.yaml'),
            prompt_file.with_suffix('.test.jsonl')
        ]
        
        for candidate in test_file_candidates:
            if candidate.exists():
                test_file = candidate
                console.print(f"[cyan]📋 Using test file: {test_file}[/cyan]")
                break
    
    # Load or generate tests
    if test_file and test_file.exists():
        if test_file.suffix == '.jsonl':
            tests = []
            with open(test_file, 'r') as f:
                for line in f:
                    tests.append(json.loads(line))
        else:
            test_data = load_prompt_file(test_file)
            tests = test_data.get('tests', [])
    else:
        console.print("[yellow]⚠️ No test file found. Generating synthetic tests...[/yellow]")
        tests = evaluator.generate_tests(prompt_data, count=num_tests)
    
    # Run tests
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Running {len(tests)} tests...", total=len(tests))
        
        run_result = evaluator.run_tests(
            prompt_data,
            tests[:num_tests],
            model=model,
            progress_callback=lambda: progress.advance(task)
        )
    
    # Display results
    display_test_results(run_result, save_results, prompt_file.stem)
    
    # Display performance results if available
    if 'performance_results' in run_result:
        display_performance_results(run_result['performance_results'])

def testcomp_command(
    prompt_file: Path = typer.Argument(..., help="Path to the prompt file"),
    test_file: Path = typer.Argument(..., help="Path to comprehensive test file"),
    aspects: Optional[str] = typer.Option(None, "--aspects", "-a", help="Comma-separated evaluation aspects"),
    models: Optional[str] = typer.Option(None, "--models", "-m", help="Comma-separated list of models"),
    save_results: bool = typer.Option(True, "--save-results", "-s", help="Save evaluation results"),
    threshold: float = typer.Option(7.0, "--threshold", "-t", help="Minimum score threshold")
):
    """🔬 Run comprehensive multi-aspect evaluation"""
    console.print(f"[bold blue]🔬 Running comprehensive evaluation for: {prompt_file}[/bold blue]")
    
    # Load prompt and tests
    prompt_data = load_prompt_file(prompt_file)
    test_data = load_prompt_file(test_file)
    
    # Parse aspects and models
    aspect_list = aspects.split(",") if aspects else None
    model_list = models.split(",") if models else None
    
    # Initialize evaluator
    project = PBTProject()
    evaluator = ComprehensiveEvaluator(project)
    
    # Run comprehensive evaluation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Running comprehensive evaluation...", total=1)
        
        results = evaluator.evaluate_comprehensive(
            prompt_data,
            test_data.get('tests', []),
            aspects=aspect_list,
            models=model_list
        )
        
        progress.update(task, completed=1)
    
    # Display results
    if results['success']:
        scores = results['scores']
        
        # Create results table
        table = Table(title="Comprehensive Evaluation Results", show_header=True, header_style="bold magenta")
        table.add_column("Aspect", style="cyan", no_wrap=True)
        table.add_column("Score", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Details")
        
        overall_score = 0
        aspect_count = 0
        
        for aspect, score in scores.items():
            if isinstance(score, dict):
                score_value = score.get('score', 0)
                details = score.get('details', '')
            else:
                score_value = score
                details = ""
            
            overall_score += score_value
            aspect_count += 1
            
            status = "✅" if score_value >= threshold else "⚠️" if score_value >= 5 else "❌"
            color = "green" if score_value >= threshold else "yellow" if score_value >= 5 else "red"
            
            table.add_row(
                aspect.replace('_', ' ').title(),
                f"[{color}]{score_value:.1f}/10[/{color}]",
                status,
                details[:50] + "..." if len(details) > 50 else details
            )
        
        console.print(table)
        
        # Overall assessment
        avg_score = overall_score / aspect_count if aspect_count > 0 else 0
        console.print(f"\n[bold]🎯 OVERALL SCORE: {avg_score:.1f}/10[/bold]")
        
        if avg_score >= 8:
            console.print("[green]✅ PRODUCTION READY[/green]")
        elif avg_score >= 6:
            console.print("[yellow]⚠️ NEEDS IMPROVEMENT[/yellow]")
        else:
            console.print("[red]❌ NOT READY FOR PRODUCTION[/red]")
        
        # Save results
        if save_results:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_dir = Path("evaluations")
            results_dir.mkdir(exist_ok=True)
            results_file = results_dir / f"comprehensive_{prompt_file.stem}_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            console.print(f"\n[green]✅ Results saved to: {results_file}[/green]")
    else:
        console.print(f"[red]❌ Evaluation failed: {results.get('error', 'Unknown error')}[/red]")
        raise typer.Exit(1)

def compare_command(
    prompt_file: Path = typer.Argument(..., help="Path to the prompt file to compare"),
    models: str = typer.Option("claude,gpt-4,gpt-3.5-turbo", "--models", "-m", help="Comma-separated list of models"),
    variables: Optional[str] = typer.Option(None, "--vars", "-v", help="JSON string of variables"),
    save_results: bool = typer.Option(True, "--save-results", "-s", help="Save comparison results"),
    output_format: str = typer.Option("table", "--output", "-o", help="Output format: table, json, markdown")
):
    """🔍 Compare prompt performance across multiple models"""
    console.print(f"[bold blue]🔍 Comparing models for prompt: {prompt_file}[/bold blue]")
    
    # Parse models
    model_list = [m.strip() for m in models.split(",")]
    console.print(f"[cyan]📊 Models to compare: {', '.join(model_list)}[/cyan]")
    
    # Parse variables
    vars_dict = parse_variables(variables)
    if vars_dict:
        console.print(f"[cyan]📝 Variables: {json.dumps(vars_dict, indent=2)}[/cyan]")
    
    # Load prompt
    prompt_data = load_prompt_file(prompt_file)
    
    # Initialize project and evaluator
    project = PBTProject()
    evaluator = PromptEvaluator(project)
    
    # Compare across models
    results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Comparing {len(model_list)} models...", total=len(model_list))
        
        for model in model_list:
            model_result = evaluator.evaluate_single(
                prompt_data,
                model=model,
                variables=vars_dict
            )
            results[model] = model_result
            progress.advance(task)
    
    # Display results based on format
    if output_format == "table":
        table = Table(title="Model Comparison Results", show_header=True, header_style="bold cyan")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Response Time", justify="right")
        table.add_column("Token Count", justify="right")
        table.add_column("Score", justify="right")
        table.add_column("Output Preview")
        
        for model, result in results.items():
            if result['success']:
                output_preview = result['output'][:50] + "..." if len(result['output']) > 50 else result['output']
                table.add_row(
                    model,
                    f"{result.get('response_time', 0):.2f}s",
                    str(result.get('token_count', 'N/A')),
                    f"{result.get('score', 0):.1f}/10",
                    output_preview
                )
            else:
                table.add_row(
                    model,
                    "N/A",
                    "N/A",
                    "0.0/10",
                    f"[red]Error: {result['error']}[/red]"
                )
        
        console.print(table)
    
    elif output_format == "json":
        console.print(json.dumps(results, indent=2, default=str))
    
    elif output_format == "markdown":
        console.print("# Model Comparison Results\n")
        for model, result in results.items():
            console.print(f"## {model}")
            if result['success']:
                console.print(f"- Response Time: {result.get('response_time', 0):.2f}s")
                console.print(f"- Token Count: {result.get('token_count', 'N/A')}")
                console.print(f"- Score: {result.get('score', 0):.1f}/10")
                console.print(f"- Output: {result['output'][:200]}...")
            else:
                console.print(f"- Error: {result['error']}")
            console.print()
    
    # Save results
    if save_results:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("evaluations")
        results_dir.mkdir(exist_ok=True)
        results_file = results_dir / f"comparison_{prompt_file.stem}_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"\n[green]✅ Results saved to: {results_file}[/green]")

def validate_command(
    agents_dir: Path = typer.Option(Path("prompts"), "--dir", "-d", help="Directory containing prompts"),
    individual: bool = typer.Option(False, "--individual", "-i", help="Test each prompt individually"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use for validation"),
    threshold: float = typer.Option(7.0, "--threshold", "-t", help="Minimum score threshold")
):
    """✓ Validate all prompts in a directory"""
    console.print(f"[bold blue]✓ Validating prompts in: {agents_dir}[/bold blue]")
    
    # Find all prompt files
    prompt_files = list(agents_dir.glob("*.prompt.yaml")) + list(agents_dir.glob("*.yaml"))
    
    if not prompt_files:
        console.print("[yellow]⚠️ No prompt files found[/yellow]")
        raise typer.Exit(0)
    
    console.print(f"[cyan]Found {len(prompt_files)} prompt files[/cyan]")
    
    # Initialize evaluator
    project = PBTProject()
    evaluator = PromptEvaluator(project)
    
    # Validation results
    results = {
        "total": len(prompt_files),
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "details": {}
    }
    
    # Validate each prompt
    for prompt_file in prompt_files:
        console.print(f"\n[cyan]Validating: {prompt_file.name}[/cyan]")
        
        try:
            prompt_data = load_prompt_file(prompt_file)
            
            # Basic validation
            validation_result = evaluator.validate_prompt(prompt_data)
            
            if validation_result['valid']:
                # Run basic test if individual testing is enabled
                if individual:
                    test_result = evaluator.evaluate_single(
                        prompt_data,
                        model=model
                    )
                    
                    if test_result['success'] and test_result.get('score', 0) >= threshold:
                        console.print(f"[green]✅ {prompt_file.name} - PASSED (Score: {test_result['score']:.1f}/10)[/green]")
                        results["passed"] += 1
                    else:
                        console.print(f"[red]❌ {prompt_file.name} - FAILED (Score: {test_result.get('score', 0):.1f}/10)[/red]")
                        results["failed"] += 1
                else:
                    console.print(f"[green]✅ {prompt_file.name} - Valid structure[/green]")
                    results["passed"] += 1
            else:
                console.print(f"[red]❌ {prompt_file.name} - Invalid: {validation_result['errors']}[/red]")
                results["failed"] += 1
                
        except Exception as e:
            console.print(f"[red]❌ {prompt_file.name} - Error: {str(e)}[/red]")
            results["errors"] += 1
    
    # Summary
    console.print("\n[bold]📊 Validation Summary:[/bold]")
    console.print(f"  • Total prompts: {results['total']}")
    console.print(f"  • [green]Passed: {results['passed']}[/green]")
    console.print(f"  • [red]Failed: {results['failed']}[/red]")
    console.print(f"  • [red]Errors: {results['errors']}[/red]")
    
    # Exit with error if any failed
    if results["failed"] > 0 or results["errors"] > 0:
        raise typer.Exit(1)